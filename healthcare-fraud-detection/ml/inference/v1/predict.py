import os
import sys
import pandas as pd
import numpy as np

# Resolve path dependencies
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.append(CURRENT_DIR)

from model_loader import load_artifacts
from explainability import generate_reasons

# Load singletons
model, preprocessor = load_artifacts()

def feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply feature engineering logic matching deep learning training pipeline.
    """
    df = df.copy()

    # 1. Approval Ratio
    df["Approval_Ratio"] = df["Approved_Amount"] / (df["Claim_Amount"] + 1)

    # 2. High Claim Flag
    df["High_Claim"] = (df["Claim_Amount"] > 700).astype(int)

    # 3. Long Stay Flag
    df["Long_Stay"] = (df["Length_of_Stay"] >= 7).astype(int)

    # 4. Frequent Visitor Flag
    df["Frequent_Visitor"] = (df["Prior_Visits_12m"] >= 5).astype(int)

    # 5. High Provider Load Flag
    df["High_Provider_Load"] = (df["Number_of_Claims_Per_Provider_Monthly"] >= 70).astype(int)

    # 6. Risk Score
    df["Risk_Score"] = (
        df["High_Claim"]
        + df["Long_Stay"]
        + df["Frequent_Visitor"]
        + df["High_Provider_Load"]
    )

    return df

def predict_claim(claim_data: dict) -> dict:
    """
    Consolidated Keras deep learning inference engine.
    """
    # Create DataFrame (single row)
    df = pd.DataFrame([claim_data])

    # Apply Feature Engineering
    df_engineered = feature_engineering(df)

    # Transform numerical and categorical columns
    X_processed = preprocessor.transform(df_engineered)

    # Predict using Keras model
    probability = float(model.predict(X_processed, verbose=0)[0][0])

    # Prediction Label
    label = "Fraud" if probability >= 0.5 else "Not Fraud"

    # Confidence
    confidence = probability if probability >= 0.5 else (1 - probability)

    # Risk level threshold logic: <30% Low, 30%-70% Medium, >=70% High
    percent = probability * 100
    if percent < 30:
        risk_level = "Low"
    elif percent < 70:
        risk_level = "Medium"
    else:
        risk_level = "High"

    # Generate explanations
    reasons = generate_reasons(claim_data)

    return {
        "predicted_label": label,
        "fraud_probability": round(probability, 4),
        "risk_level": risk_level,
        "confidence": round(confidence, 4),
        "reasons": reasons,
        "model_version": "TensorFlow-Keras-v1.0.0"
    }
