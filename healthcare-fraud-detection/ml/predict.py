import os
# pyrefly: ignore [missing-import]
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

# Resolve paths relative to this file
BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "best_model.pkl"
PREPROCESSOR_PATH = BASE_DIR / "models" / "preprocessor.pkl"
CLAIM_LIMIT_PATH = BASE_DIR / "models" / "claim_threshold.pkl"
PROVIDER_LIMIT_PATH = BASE_DIR / "models" / "provider_threshold.pkl"

# Global lazy-loaded objects
_model = None
_preprocessor = None
_claim_threshold = 711.365
_provider_threshold = 72.0

def load_artifacts():
    """
    Load model, preprocessor, and threshold pickles if they are not already loaded.
    """
    global _model, _preprocessor, _claim_threshold, _provider_threshold
    
    if _model is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(f"Model file not found at: {MODEL_PATH}")
        _model = joblib.load(MODEL_PATH)
        
    if _preprocessor is None:
        if not PREPROCESSOR_PATH.exists():
            raise FileNotFoundError(f"Preprocessor file not found at: {PREPROCESSOR_PATH}")
        _preprocessor = joblib.load(PREPROCESSOR_PATH)
        
    if CLAIM_LIMIT_PATH.exists():
        try:
            _claim_threshold = float(joblib.load(CLAIM_LIMIT_PATH))
        except Exception:
            pass
            
    if PROVIDER_LIMIT_PATH.exists():
        try:
            _provider_threshold = float(joblib.load(PROVIDER_LIMIT_PATH))
        except Exception:
            pass


def feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply matching feature engineering logic used during model training.
    """
    # 1. Approval Ratio
    df["Approval_Ratio"] = df["Approved_Amount"] / (df["Claim_Amount"] + 1)
    
    # 2. High Claim Flag
    df["High_Claim"] = (df["Claim_Amount"] > _claim_threshold).astype(int)
    
    # 3. Age Group Categorical
    df["Age_Group"] = pd.cut(
        df["Patient_Age"],
        bins=[0, 18, 35, 50, 65, 100],
        labels=["Child", "Young", "Adult", "Middle", "Senior"],
        include_lowest=True
    )
    
    # 4. Long Hospital Stay Flag
    df["Long_Stay"] = (df["Length_of_Stay"] >= 7).astype(int)
    
    # 5. Frequent Visitor Flag
    df["Frequent_Visitor"] = (df["Prior_Visits_12m"] >= 5).astype(int)
    
    # 6. High Provider Load Flag
    df["High_Provider_Load"] = (df["Number_of_Claims_Per_Provider_Monthly"] > _provider_threshold).astype(int)
    
    # 7. Claim Submission Delay Categorical
    df["Claim_Delay"] = pd.cut(
        df["Days_Between_Service_and_Claim"],
        bins=[0, 7, 15, 30, 365],
        labels=["Quick", "Normal", "Late", "Very Late"],
        include_lowest=True
    )
    
    # 8. Composite Risk Score
    df["Risk_Score"] = df["High_Claim"] + df["Long_Stay"] + df["Frequent_Visitor"] + df["High_Provider_Load"]
    
    return df


def generate_explanations(raw_data: dict, prob: float, risk_level: str) -> list[str]:
    """
    Generate natural language explanations explaining the risk score.
    """
    reasons = []
    
    claim_amount = float(raw_data.get("Claim_Amount", 0))
    approved_amount = float(raw_data.get("Approved_Amount", 0))
    stay = int(raw_data.get("Length_of_Stay", 0))
    visits = int(raw_data.get("Prior_Visits_12m", 0))
    provider_claims = int(raw_data.get("Number_of_Claims_Per_Provider_Monthly", 0))
    
    if claim_amount > _claim_threshold:
        reasons.append(f"Claim amount of ${claim_amount:,.2f} is higher than the normal threshold (${_claim_threshold:,.2f}).")
        
    if stay >= 7:
        reasons.append(f"Patient stay length of {stay} days is unusually high (average is under 5 days).")
        
    if visits >= 5:
        reasons.append(f"Patient has a high visit frequency of {visits} visits in the last 12 months.")
        
    if provider_claims > _provider_threshold:
        reasons.append(f"Healthcare provider has a high monthly volume of {provider_claims} claims.")
        
    if claim_amount > 0 and (approved_amount / claim_amount) < 0.50:
        reasons.append(f"Claim has a very low approval ratio (only {(approved_amount/claim_amount)*100:.1f}% approved).")
        
    if not reasons and prob > 0.50:
        reasons.append("Model detected suspicious co-occurrence pattern of procedure codes and diagnosis codes.")
        
    return reasons


def predict_claim(claim_data: dict) -> dict:
    """
    Load artifacts, preprocess raw data, perform feature engineering,
    run model inference, and assign business risk levels.
    """
    # Ensure model and preprocessor are loaded
    load_artifacts()

    # Normalize input fields to match expected raw column names
    # Support both database snake_case and frontend camelCase
    normalized = {
        "Patient_Age": int(claim_data.get("Patient_Age", claim_data.get("age", 45))),
        "Patient_Gender": str(claim_data.get("Patient_Gender", claim_data.get("gender", "Male"))).capitalize(),
        "Diagnosis_Code": str(claim_data.get("Diagnosis_Code", claim_data.get("diagnosis", "I10"))),
        "Procedure_Code": int(claim_data.get("Procedure_Code", 99213)),
        "Claim_Amount": float(claim_data.get("Claim_Amount", claim_data.get("claimAmount", 150.0))),
        "Approved_Amount": float(claim_data.get("Approved_Amount", claim_data.get("claimAmount", 120.0) * 0.8)),
        "Insurance_Type": str(claim_data.get("Insurance_Type", "Private")),
        "Claim_Submission_Date": str(claim_data.get("Claim_Submission_Date", datetime.utcnow().strftime("%Y-%m-%d") if "datetime" in globals() else "2026-07-05")),
        "Days_Between_Service_and_Claim": int(claim_data.get("Days_Between_Service_and_Claim", 10)),
        "Number_of_Claims_Per_Provider_Monthly": int(claim_data.get("Number_of_Claims_Per_Provider_Monthly", 30)),
        "Provider_Specialty": str(claim_data.get("Provider_Specialty", "General Practice")),
        "Patient_State": str(claim_data.get("Patient_State", "TX")),
        "Claim_Status": str(claim_data.get("Claim_Status", "Pending")),
        "Length_of_Stay": int(claim_data.get("Length_of_Stay", 2)),
        "Visit_Type": str(claim_data.get("Visit_Type", "Outpatient")),
        "Chronic_Condition_Flag": int(claim_data.get("Chronic_Condition_Flag", 0)),
        "Prior_Visits_12m": int(claim_data.get("Prior_Visits_12m", 1))
    }

    # Create DataFrame (single row)
    df = pd.DataFrame([normalized])

    # Apply Feature Engineering
    df_engineered = feature_engineering(df)

    # Process columns through ColumnTransformer
    processed = _preprocessor.transform(df_engineered)

    # Predict probability
    prob = float(_model.predict_proba(processed)[0][1])
    label = "Fraud" if prob >= 0.50 else "Not Fraud"

    # Business rules for risk level and auto approval routing
    # Probability (0-100%)
    prob_percent = prob * 100
    if prob_percent < 30:
        risk_level = "Low"
    elif prob_percent < 70:
        risk_level = "Medium"
    else:
        risk_level = "High"

    reasons = generate_explanations(normalized, prob, risk_level)

    return {
        "predicted_label": label,
        "fraud_probability": round(prob, 4),
        "risk_level": risk_level,
        "confidence": round(1 - prob if prob < 0.50 else prob, 4),
        "reasons": reasons,
        "model_version": "v1.0.0"
    }
