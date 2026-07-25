import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.ensemble import IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report
import shap
import pickle

def engineer_features(df):
    print("Engineering sequential and behavioral features...")
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # 1. Temporal Features
    df['hour_of_day'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    
    # 2. Sequential & Behavioral Features (Grouped by Entity)
    # Sort chronologically to ensure sequence accuracy
    df = df.sort_values(by=['entity_id', 'timestamp'])
    
    # Time since last login
    df['time_since_last_event_sec'] = df.groupby('entity_id')['timestamp'].diff().dt.total_seconds().fillna(999999) # Fillna handles Cold Start
    
    # Did the IP or Device change from the last login?
    df['ip_changed_flag'] = (df['source_ip'] != df.groupby('entity_id')['source_ip'].shift()).astype(int)
    df['device_changed_flag'] = (df['device_fingerprint'] != df.groupby('entity_id')['device_fingerprint'].shift()).astype(int)
    
    # Velocity/Frequency (Counts in sliding windows to detect Brute Force/Stuffing)
    df['user_event_count_recent'] = df.groupby('entity_id')['timestamp'].transform(lambda x: x.diff().dt.total_seconds().lt(60).sum())
    df['ip_event_count_recent'] = df.groupby('source_ip')['timestamp'].transform(lambda x: x.diff().dt.total_seconds().lt(60).sum())

    # Encode categorical variables
    categorical_cols = ['entity_type', 'auth_method', 'resource_accessed']
    encoders = {}
    for col in categorical_cols:
        le = LabelEncoder()
        df[col + '_encoded'] = le.fit_transform(df[col].astype(str))
        encoders[col] = le
        
    return df, encoders

def train_pipeline():
    df = pd.read_csv('synthetic_access_logs.csv')
    df, encoders = engineer_features(df)
    
    # Define feature set
    features = [
        'hour_of_day', 'day_of_week', 'time_since_last_event_sec', 
        'ip_changed_flag', 'device_changed_flag', 'session_duration',
        'user_event_count_recent', 'ip_event_count_recent',
        'entity_type_encoded', 'auth_method_encoded', 'resource_accessed_encoded'
    ]
    
    X = df[features]
    
    # Encode target labels
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(df['label'])
    
    X_train, X_test, y_train, y_test, indices_train, indices_test = train_test_split(
        X, y, df.index, test_size=0.2, random_state=42, stratify=y
    )

    print("1. Training Baseline Profiler (Isolation Forest)...")
    iso_forest = IsolationForest(contamination=0.05, random_state=42)
    iso_forest.fit(X_train)
    # Adds unsupervised anomaly score feature (Handles unknown anomalies)
    X_train_unsupervised = X_train.copy()
    X_test_unsupervised = X_test.copy()
    X_train_unsupervised['iso_score'] = iso_forest.decision_function(X_train)
    X_test_unsupervised['iso_score'] = iso_forest.decision_function(X_test)

    print("2. Training Multi-Class Detector (XGBoost)...")
    clf = xgb.XGBClassifier(
        objective='multi:softprob',
        num_class=len(label_encoder.classes_),
        eval_metric='mlogloss',
        scale_pos_weight=10, # Handle class imbalance
        random_state=42
    )
    clf.fit(X_train_unsupervised, y_train)

    print("\nModel Evaluation:")
    y_pred = clf.predict(X_test_unsupervised)
    print(classification_report(y_test, y_pred, target_names=label_encoder.classes_))

    print("3. Generating SHAP Explainability Engine...")
    explainer = shap.TreeExplainer(clf)
    
    # Save test dataset and models for the Dashboard
    df_test = df.iloc[indices_test].copy()
    df_test['iso_score'] = X_test_unsupervised['iso_score'].values
    df_test['predicted_class'] = label_encoder.inverse_transform(y_pred)
    
    # Get max probability as Risk Score
    y_proba = clf.predict_proba(X_test_unsupervised)
    df_test['risk_score'] = np.max(y_proba, axis=1) * 100 
    
    df_test.to_csv('dashboard_data.csv', index=False)
    
    with open('model_pipeline.pkl', 'wb') as f:
        pickle.dump({
            'classifier': clf, 'iso_forest': iso_forest,
            'explainer': explainer, 'label_encoder': label_encoder,
            'features': list(X_train_unsupervised.columns)
        }, f)
        
    print("✅ Pipeline training complete. Models saved for Dashboard.")

if __name__ == "__main__":
    train_pipeline()