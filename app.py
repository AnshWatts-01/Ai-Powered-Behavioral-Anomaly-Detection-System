import streamlit as st
import pandas as pd
import numpy as np
import shap
import pickle
import plotly.express as px


st.set_page_config(page_title="SOC Anomaly Dashboard", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv('dashboard_data.csv')
    
    # FIX: Convert string timestamps back into real datetime objects
    df['timestamp'] = pd.to_datetime(df['timestamp']) 
    
    # Filter only anomalies for the alert queue
    anomalies = df[df['predicted_class'] != 'normal'].sort_values('risk_score', ascending=False)
    
    with open('model_pipeline.pkl', 'rb') as f:
        pipeline = pickle.load(f)
        
    return df, anomalies, pipeline

df, anomalies, pipeline = load_data()

st.title("🛡️ AI-Powered Behavioral Anomaly Detection System")
st.markdown("Monitor real-time access logs, detect lateral movement, device spoofing, and brute force attacks.")
# --- GLOBAL CUSTOM TECH THEME CSS ---
# This forces the dark theme for anyone running the app, bypassing local browser/config settings.
st.markdown("""
<style>
    /* Global App Background & Text */
    .stApp {
        background-color: #0A0E17; /* Deep cyber navy/black */
        color: #C0C0C0; /* Light grey text for readability */
    }
    
    /* Top Header (Make it transparent so it doesn't show a white bar) */
    [data-testid="stHeader"] {
        background-color: rgba(0,0,0,0);
    }

    /* Global Typography & Headings */
    h1, h2, h3 {
        color: #00FFAA !important; /* Neon cyber green */
        text-shadow: 0 0 8px rgba(0, 255, 170, 0.3);
        font-family: 'Courier New', Courier, monospace; /* Techy font for headers */
    }

    /* Glowing Metric Boxes */
    [data-testid="stMetric"] {
        background-color: #111827;
        border: 1px solid #00FFAA;
        box-shadow: 0 0 15px rgba(0, 255, 170, 0.15);
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #00FFAA;
    }
    
    /* Force Metric Labels to be bright white */
    [data-testid="stMetricLabel"] * {
        color: #FFFFFF !important; 
        font-size: 16px !important;
    }

    /* Neon Metric Numbers */
    [data-testid="stMetricValue"] {
        color: #00FFAA !important;
        text-shadow: 0 0 10px rgba(0, 255, 170, 0.5);
    }
    
    /* Customizing the DataFrame Header & Styling */
    thead tr th {
        background-color: #111827 !important;
        color: #00FFAA !important;
        border-bottom: 1px solid #00FFAA !important;
    }
    tbody tr th {
        background-color: #0A0E17 !important;
        color: #C0C0C0 !important;
    }
    
    /* Selectbox & Dropdown styling */
    div[data-baseweb="select"] > div {
        background-color: #111827;
        color: #00FFAA;
        border: 1px solid #00FFAA;
    }
    
    /* Dividers (st.divider) */
    hr {
        border-bottom-color: #00FFAA !important;
        opacity: 0.3;
    }

    /* Aggressive Fix for ALL Labels, Selectboxes, and Paragraph Text */
    label, p, [data-testid="stWidgetLabel"] *, .stMarkdown p {
        color: #E2E8F0 !important; /* Bright light slate/white */
        font-size: 15px !important;
    }
</style>
""", unsafe_allow_html=True)
# ------------------------------------


# 1. High-Level Metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Events Evaluated", len(df))
col2.metric("High-Risk Alerts Detected", len(anomalies[anomalies['risk_score'] > 85]))
col3.metric("Total Anomalies", len(anomalies))
col4.metric("Active Threat Types", anomalies['predicted_class'].nunique())

st.divider()

# 2. Ranked Alert Queue
st.subheader("🚨 Ranked Alert Queue")
st.markdown("Prioritized list of detected anomalies. Click an Entity ID below for explainability.")

display_cols = ['timestamp', 'entity_id', 'entity_type', 'source_ip', 'predicted_class', 'risk_score']
st.dataframe(
    anomalies[display_cols].style.background_gradient(subset=['risk_score'], cmap='Reds'),
    use_container_width=True
)

st.divider()

# 3. Explainability & Deep Dive
st.subheader("🔍 Alert Explainability Layer")
selected_entity = st.selectbox("Select an anomalous Entity ID to investigate:", anomalies['entity_id'].unique())

if selected_entity:
    entity_data = anomalies[anomalies['entity_id'] == selected_entity].iloc[0]
    
    col_info, col_shap = st.columns([1, 2])
    
    # --- Re-construct features for SHAP ---
    X_instance = entity_data[pipeline['features']].to_frame().T.astype(float)
    explainer = pipeline['explainer']
    shap_values = explainer.shap_values(X_instance)
    class_idx = pipeline['label_encoder'].transform([entity_data['predicted_class']])[0]
    
    # Extract the SHAP values safely
    if isinstance(shap_values, list):
        sv_for_class = shap_values[class_idx]
    elif len(shap_values.shape) == 3:
        sv_for_class = shap_values[:, :, class_idx]
    else:
        sv_for_class = shap_values
        
    # Flatten array for the single row
    sv_flat = sv_for_class[0] if len(sv_for_class.shape) > 1 else sv_for_class
    
    # Create a DataFrame mapping features to their SHAP impact
    impact_df = pd.DataFrame({
        'Feature': pipeline['features'],
        'SHAP Impact': sv_flat,
        'Absolute Impact': np.abs(sv_flat),
        'Actual Value': X_instance.iloc[0].values
    }).sort_values(by='Absolute Impact', ascending=False)

    top_features = impact_df.head(3)
    threat_type = entity_data['predicted_class'].replace('_', ' ').title()

    # --- LEFT COLUMN: Human-Readable Insights ---
    with col_info:
        st.markdown("### 🧠 AI Analysis Report")
        st.error(f"**Threat Detected:** {threat_type}")
        st.markdown("**Key Indicators:**")
        
        # Generate plain English explanations for the top 3 anomalies
        for _, row in top_features.iterrows():
            if row['SHAP Impact'] > 0:
                st.markdown(f"- 🔴 **{row['Feature']}** was dangerously abnormal (Value recorded: **{row['Actual Value']:.2f}**).")
            else:
                st.markdown(f"- 🟢 **{row['Feature']}** lowered the overall risk (Value recorded: **{row['Actual Value']:.2f}**).")

    
    with col_shap:
        st.markdown("### 📊 Feature Attribution")
        
        # Prepare data for a horizontal bar chart (take top 8 features for cleanliness)
        plot_df = impact_df.head(8).sort_values(by='Absolute Impact', ascending=True)
        
        fig_shap = px.bar(
            plot_df, 
            x='SHAP Impact', 
            y='Feature', 
            orientation='h',
            text='Actual Value', # Shows the raw number directly on the bar
            hover_data=['Actual Value']
        )
        
        # Color bars red if they push towards anomaly, green if they push towards normal
        colors = np.where(plot_df['SHAP Impact'] > 0, '#FF4B4B', '#00FFAA')
        fig_shap.update_traces(marker_color=colors, texttemplate='%{text:.2f}', textposition='outside')
        
      
        fig_shap.update_layout(
            template="plotly_dark",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            xaxis_title="Impact on AI Decision",
            yaxis_title="",
            height=350
        )
        
        st.plotly_chart(fig_shap, use_container_width=True)

    st.divider()

    # 4. Entity History View
    st.subheader(f"Timeline History for {selected_entity}")
    history_df = df[df['entity_id'] == selected_entity].sort_values('timestamp')
    
    # Scatter plot for point-in-time events
    fig2 = px.scatter(
        history_df, 
        x="timestamp", 
        y="resource_accessed", 
        color="predicted_class",
        hover_data=["source_ip", "device_fingerprint"],
        size_max=15
    )
    
   
    fig2.update_traces(marker=dict(size=12, opacity=0.8, line=dict(width=1, color='#00FFAA')))
    
   
    fig2.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=True, gridcolor='#333333'),
        yaxis=dict(showgrid=True, gridcolor='#333333'),
        legend_title_font_color="#FFFFFF",
        legend_font_color="#FFFFFF"        
    )
    
   
    st.plotly_chart(fig2, theme=None, use_container_width=True)