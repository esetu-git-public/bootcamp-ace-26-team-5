import pandas as pd
import numpy as np
from .load_model import load_artifacts

# Load model and preprocessor
model, preprocessor = load_artifacts()


# ==========================================================
# Feature Engineering
# ==========================================================

def feature_engineering(df):

    df = df.copy()

    # Approval Ratio
    df["Approval_Ratio"] = df["Approved_Amount"] / (df["Claim_Amount"] + 1)

    # High Claim
    df["High_Claim"] = (
        df["Claim_Amount"] > 700
    ).astype(int)

    # Long Stay
    df["Long_Stay"] = (
        df["Length_of_Stay"] >= 7
    ).astype(int)

    # Frequent Visitor
    df["Frequent_Visitor"] = (
        df["Prior_Visits_12m"] >= 5
    ).astype(int)

    # High Provider Load
    df["High_Provider_Load"] = (
        df["Number_of_Claims_Per_Provider_Monthly"] >= 70
    ).astype(int)

    # Risk Score
    df["Risk_Score"] = (
        df["High_Claim"]
        + df["Long_Stay"]
        + df["Frequent_Visitor"]
        + df["High_Provider_Load"]
    )

    return df
# ==========================================================
# Fraud Prediction Function
# ==========================================================

def predict_claim(claim_data: dict):

    # Convert JSON to DataFrame
    df = pd.DataFrame([claim_data])

    # Feature Engineering
    df = feature_engineering(df)

    # Preprocess
    X_processed = preprocessor.transform(df)

    # Predict Probability
    probability = float(model.predict(X_processed, verbose=0)[0][0])

    # Prediction Label
    prediction = "Fraud" if probability >= 0.5 else "Not Fraud"

    # Confidence
    confidence = probability if probability >= 0.5 else (1 - probability)

    # Risk Level
    percent = probability * 100

    if percent < 30:
        risk = "Low"

    elif percent < 70:
        risk = "Medium"

    else:
        risk = "High"

    reasons = []

    if claim_data.get("Claim_Amount", 0) > 700:
        reasons.append("High Claim Amount")

    if claim_data.get("Prior_Visits_12m", 0) >= 5:
        reasons.append("Frequent Previous Visits")

    if claim_data.get("Length_of_Stay", 0) >= 7:
        reasons.append("Long Hospital Stay")

    if claim_data.get("Number_of_Claims_Per_Provider_Monthly", 0) >= 70:
        reasons.append("High Provider Claim Volume")

    if len(reasons) == 0:
        reasons.append("No significant fraud indicators detected.")

    return {

        "prediction": prediction,

        "fraud_probability": round(probability * 100, 2),

        "risk_level": risk,

        "confidence": round(confidence * 100, 2),

        "reasons": reasons,

        "model_version": "TensorFlow-Keras-v1"

    }
# ==========================================================
# Test Prediction
# ==========================================================

if __name__ == "__main__":

    sample_claim = {

        "Patient_Age": 45,
        "Patient_Gender": "Male",
        "Diagnosis_Code": "I10",
        "Procedure_Code": 99213,
        "Claim_Amount": 850,
        "Approved_Amount": 500,
        "Insurance_Type": "Private",
        "Claim_Submission_Date": "2026-07-09",
        "Days_Between_Service_and_Claim": 10,
        "Number_of_Claims_Per_Provider_Monthly": 85,
        "Provider_Specialty": "General Practice",
        "Patient_State": "TX",
        "Claim_Status": "Pending",
        "Length_of_Stay": 8,
        "Visit_Type": "Inpatient",
        "Chronic_Condition_Flag": 1,
        "Prior_Visits_12m": 6

    }

    result = predict_claim(sample_claim)

    print("\n========== Prediction Result ==========")

    for key, value in result.items():
        print(f"{key}: {value}")

    print("=======================================\n")