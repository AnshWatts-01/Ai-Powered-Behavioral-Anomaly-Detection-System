# 🛡️ AI-Powered Behavioral Anomaly Detection System

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Scikit-Learn](https://img.shields.io/badge/Scikit_Learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)

> **An intelligent Security Operations Center (SOC) dashboard built to monitor, detect, and explain cybersecurity threats in real-time.** 

## 🎯 Project Overview

Modern cyber threats like lateral movement, device spoofing, and brute force attacks often bypass traditional rule-based security. This project leverages Machine Learning (XGBoost) to detect behavioral anomalies in access logs. 

To ensure security analysts can trust the AI, the system integrates **Explainable AI (XAI)** via SHAP, providing human-readable, transparent insights into exactly *why* an event was flagged.

## ⚙️ Architectural Decisions & Assumptions

To align with the rigorous requirements of a real-time Security Operations Center (SOC) and the project deliverables, the following strategic design choices were made:

* **Baseline Profiling Representation:** Per-entity "normal" behavior is established through our feature engineering pipeline prior to classification. By tracking historical statistical profiles (e.g., standard login hours, typical geographic velocity, and average session durations per entity ID), deviations from these baselines are explicitly passed to the detection model to flag anomalies.
* **Strategic Model Selection (Sequence-Awareness):** While native deep learning sequence models (LSTMs, GRUs, or Transformers) are traditional for temporal data, we strategically opted for **XGBoost**. Deep learning models often introduce high inference latency and demand heavy GPU compute. To fulfill the requirement of sequence-awareness without the computational overhead, we engineered sequential, time-based features (such as `time_since_last_event_sec` and `user_event_count_recent`). This allows our lightweight classifier to understand the temporal context of user behavior while maintaining the millisecond-level inference times critical for live SOC dashboards running on standard hardware.

## ✨ Key Features

* **Dark-Themed Cyber UI:** A fully custom, distraction-free interface optimized for SOC environments.
* **Ranked Alert Queue:** Automatically prioritizes threats based on an AI-calculated risk score so analysts know what to investigate first.
* **Interactive Explainability (SHAP):** Visualizes the exact features (e.g., failed logins, unusual hours) that drove the AI's decision.
* **Entity Timeline Tracking:** Tracks specific users or devices across time using interactive Plotly visualizations to spot lateral movement.

## 💡 Implementation & Presentation Highlights

* **Custom UI Engineering:** Implemented aggressive CSS targeting to override Streamlit's default styling. This ensures a high-contrast, dark "Tech/Cyber" theme that perfectly integrates with custom Plotly charts without text visibility issues.
* **Transparent AI Logic:** The core implementation focuses not just on threat detection, but on human-readable interpretation. By using SHAP, the dashboard bridges the gap between raw machine learning predictions and actionable insights for security teams.
* **Professional Development Lifecycle:** The project is structured cleanly into three stages (Data Generation -> Model Training -> Deployment). This modular approach demonstrates strong software engineering practices and aligns perfectly with technical presentation requirements.

---

## 📂 Project Architecture

This project is separated into a clean, 3-step pipeline:

1. **`generate_data.py`**: Simulates realistic network traffic, access logs, and injects anomalies to create the `dashboard_data.csv` dataset.
2. **`train_model.py`**: Processes the data, trains an XGBoost classifier, configures the SHAP explainer, and exports the `model_pipeline.pkl`.
3. **`app.py`**: The Streamlit frontend that consumes the data and model to render the interactive dashboard.

---

## 🚀 How to Run the Project

```bash
# 1. Install Dependencies
pip install -r requirements.txt

# 2. Run the Dashboard (Quick Start)
# Uses pre-generated dataset (dashboard_data.csv) and pre-trained model (model_pipeline.pkl)
streamlit run app.py

# 3. Rebuilding the Project (End-to-End Pipeline)
# Run this full sequence to regenerate synthetic logs, retrain the AI model, and launch the app:
python generate_data.py
python train_model.py
streamlit run app.py
## 🛠️ Technology Stack

| Component | Technology |
| :--- | :--- |
| **Frontend/UI** | Streamlit, Custom CSS |
| **Data Processing** | Pandas, NumPy |
| **Machine Learning** | Scikit-Learn, XGBoost |
| **Explainable AI** | SHAP (SHapley Additive exPlanations) |
| **Data Visualization** | Plotly Express | 

