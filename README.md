# 🛡️ AI-Powered Behavioral Anomaly Detection System

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Scikit-Learn](https://img.shields.io/badge/Scikit_Learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)

> **An intelligent Security Operations Center (SOC) dashboard built to monitor, detect, and explain cybersecurity threats in real-time.** 

## 🎯 Project Overview

Modern cyber threats like lateral movement, device spoofing, and brute force attacks often bypass traditional rule-based security. This project leverages Machine Learning (XGBoost) to detect behavioral anomalies in access logs. 

To ensure security analysts can trust the AI, the system integrates **Explainable AI (XAI)** via SHAP, providing human-readable, transparent insights into exactly *why* an event was flagged.

## ✨ Key Features

*   **Dark-Themed Cyber UI:** A fully custom, distraction-free interface optimized for SOC environments.
*   **Ranked Alert Queue:** Automatically prioritizes threats based on an AI-calculated risk score so analysts know what to investigate first.
*   **Interactive Explainability (SHAP):** Visualizes the exact features (e.g., failed logins, unusual hours) that drove the AI's decision.
*   **Entity Timeline Tracking:** Tracks specific users or devices across time using interactive Plotly visualizations to spot lateral movement.

## 💡 Implementation & Presentation Highlights

*   **Custom UI Engineering:** Implemented aggressive CSS targeting to override Streamlit's default styling. This ensures a high-contrast, dark "Tech/Cyber" theme that perfectly integrates with custom Plotly charts without text visibility issues.
*   **Transparent AI Logic:** The core implementation focuses not just on threat detection, but on human-readable interpretation. By using SHAP, the dashboard bridges the gap between raw machine learning predictions and actionable insights for security teams.
*   **Professional Development Lifecycle:** The project is structured cleanly into three stages (Data Generation -> Model Training -> Deployment). This modular approach demonstrates strong software engineering practices and aligns perfectly with technical presentation requirements.

---

## 📂 Project Architecture

This project is separated into a clean, 3-step pipeline:

1.  **`generate_data.py`**: Simulates realistic network traffic, access logs, and injects anomalies to create the `dashboard_data.csv` dataset.
2.  **`train_model.py`**: Processes the data, trains an XGBoost classifier, configures the SHAP explainer, and exports the `model_pipeline.pkl`.
3.  **`app.py`**: The Streamlit frontend that consumes the data and model to render the interactive dashboard.

---

## 🚀 How to Run the Project

### 1. Install Dependencies
Before running any scripts, ensure your Python environment has the necessary libraries installed:
```bash
pip install -r requirements.txt
```

### 2. Run the Dashboard (Quick Start)
This repository includes pre-generated data (`dashboard_data.csv`) and a pre-trained model (`model_pipeline.pkl`). To view the dashboard immediately without retraining the model, simply run:
```bash
streamlit run app.py
```

### 3. Rebuilding the Project (End-to-End Pipeline)
If you want to test the full data pipeline—generating fresh synthetic logs, retraining the AI model from scratch, and launching the app—you can run this single chain command:
```bash
python generate_data.py
python train_model.py
streamlit run app.py
```

---

## 🛠️ Technology Stack

| Component | Technology |
| :--- | :--- |
| **Frontend/UI** | Streamlit, Custom CSS |
| **Data Processing** | Pandas, NumPy |
| **Machine Learning** | Scikit-Learn, XGBoost |
| **Explainable AI** | SHAP (SHapley Additive exPlanations) |
| **Data Visualization** | Plotly Express |

---
