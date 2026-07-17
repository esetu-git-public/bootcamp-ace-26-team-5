import os
import sys
import pandas as pd
import numpy as np
from utils.logger import logger

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
    Consolidated hybrid inference engine combining Keras Deep Learning and Smart Business Rules.
    """
    logger.info(f"[ML PIPELINE] Received claim data: {claim_data}")
    
    # Create DataFrame (single row)
    df = pd.DataFrame([claim_data])

    # Apply Feature Engineering
    df_engineered = feature_engineering(df)
    logger.info(f"[ML PIPELINE] Feature engineered columns: {df_engineered.to_dict(orient='records')[0]}")

    # Transform numerical and categorical columns
    X_processed = preprocessor.transform(df_engineered)
    logger.info(f"[ML PIPELINE] Preprocessing transformation complete. Input shape: {X_processed.shape}")

    # Predict using Keras model (Raw Deep Learning Probability)
    raw_probability = float(model.predict(X_processed, verbose=0)[0][0])
    logger.info(f"[ML PIPELINE] Raw neural network probability output: {raw_probability:.6f}")

    # Extract verification metrics
    risk_score = int(df_engineered["Risk_Score"].iloc[0])
    claim_amount = float(df_engineered["Claim_Amount"].iloc[0])
    length_of_stay = int(df_engineered["Length_of_Stay"].iloc[0])
    prior_visits = int(claim_data.get("Prior_Visits_12m", 1))
    provider_claims = int(claim_data.get("Number_of_Claims_Per_Provider_Monthly", 30))

    # Calculate Business Rule Score (Complementary adjustments based on strong risk evidence)
    br_adjustment = 0.0
    reasons = []

    if claim_amount > 5000:
        br_adjustment += 0.15
        reasons.append("High Claim Amount")
        if claim_amount > 20000:
            br_adjustment += 0.15  # total +0.30

    if length_of_stay >= 7:
        br_adjustment += 0.15
        reasons.append("Long Hospital Stay")
        if length_of_stay >= 30:
            br_adjustment += 0.15  # total +0.30

    if prior_visits >= 5:
        br_adjustment += 0.10
        reasons.append("Frequent Claims")

    if provider_claims >= 70:
        br_adjustment += 0.10
        reasons.append("Provider Risk")

    if risk_score >= 2:
        br_adjustment += 0.10

    # Cap business rule score adjustment
    br_adjustment = min(0.45, br_adjustment)

    # Combine DL Probability and Business Rule Score
    final_probability = raw_probability + br_adjustment

    # Sigmoid Saturation Guardrail: prevent extreme outlier bypass
    if (length_of_stay >= 7 or claim_amount > 5000 or risk_score >= 2) and final_probability < 0.30:
        final_probability = 0.75
        br_adjustment = final_probability - raw_probability
        if "High Claim Amount" not in reasons and claim_amount > 5000:
            reasons.append("High Claim Amount")
        if "Long Hospital Stay" not in reasons and length_of_stay >= 7:
            reasons.append("Long Hospital Stay")

    # Clamp probability to valid range [0.01, 0.99]
    final_probability = min(0.99, max(0.01, final_probability))

    # Prediction Label
    label = "Fraud" if final_probability >= 0.50 else "Not Fraud"

    # Confidence
    confidence = final_probability if final_probability >= 0.50 else (1 - final_probability)

    # Risk level threshold logic: <30% Low, 30%-70% Medium, >=70% High
    percent = final_probability * 100
    if percent < 30:
        risk_level = "Low"
    elif percent < 70:
        risk_level = "Medium"
    else:
        risk_level = "High"

    # Generate model explanations and merge with business rule indicators
    ml_reasons = generate_reasons(claim_data)
    for r in ml_reasons:
        if r not in reasons:
            reasons.append(r)

    if not reasons:
        reasons.append("No significant fraud indicators detected.")

    logger.info(
        f"[ML PIPELINE] Final Prediction: Label={label}, RawDL={raw_probability:.4f}, "
        f"BRAdjustment={br_adjustment:.4f}, CombinedProb={final_probability:.4f}, "
        f"Risk={risk_level}, Reasons={reasons}"
    )

    return {
        "predicted_label": label,
        "raw_probability": round(raw_probability, 4),
        "business_rule_adjustment": round(br_adjustment, 4),
        "fraud_probability": round(final_probability, 4),
        "risk_level": risk_level,
        "confidence": round(confidence, 4),
        "reasons": reasons,
        "model_version": "TensorFlow-Keras-v1.0.0"
    }

def get_model_health_status() -> dict:
    """
    Returns loaded model details and health status check.
    """
    global model
    return {
        "model_loaded": model is not None,
        "model_version": "TensorFlow-Keras-v1.0.0",
        "backend": "Keras 3 (PyTorch Backend)",
        "status": "healthy"
    }
