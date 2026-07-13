import os
import sys
import pandas as pd
from datetime import datetime

# Set Keras backend prior to Keras imports
os.environ["KERAS_BACKEND"] = "torch"

from ml.inference.v1.model_loader import load_artifacts
from ml.inference.v1.feature_engineering import run_feature_engineering
from ml.inference.v1.explainability import generate_explainability_report

def predict_claim(claim_data: dict, explain_level: str = "simple") -> dict:
    """
    Main model inference entrypoint for Keras Neural Network classifier.
    
    Args:
        claim_data (dict): Raw claim properties from Flask request body.
        explain_level (str): Level of explainability to compute.
        
    Returns:
        dict: Standard prediction response contract containing 'prediction' and 'explainability' segments.
    """
    # 1. Load compiled model assets and metadata
    model, preprocessor, metadata = load_artifacts()

    # 2. Normalize input keys to match training features
    normalized = {
        "Patient_Age": int(claim_data.get("Patient_Age", claim_data.get("age", 45))),
        "Patient_Gender": str(claim_data.get("Patient_Gender", claim_data.get("gender", "Male"))).capitalize(),
        "Diagnosis_Code": str(claim_data.get("Diagnosis_Code", claim_data.get("diagnosis", "I10"))),
        "Procedure_Code": int(claim_data.get("Procedure_Code", 99213)),
        "Claim_Amount": float(claim_data.get("Claim_Amount", claim_data.get("claimAmount", 150.0))),
        "Approved_Amount": float(claim_data.get("Approved_Amount", claim_data.get("claimAmount", 120.0) * 0.8)),
        "Insurance_Type": str(claim_data.get("Insurance_Type", "Private")),
        "Claim_Submission_Date": str(claim_data.get("Claim_Submission_Date", datetime.utcnow().strftime("%Y-%m-%d"))),
        "Days_Between_Service_and_Claim": int(claim_data.get("Days_Between_Service_and_Claim", 10)),
        "Number_of_Claims_Per_Provider_Monthly": int(claim_data.get("Number_of_Claims_Per_Provider_Monthly", 30)),
        "Provider_Specialty": str(claim_data.get("Provider_Specialty", "General Practice")),
        "Patient_State": str(claim_data.get("Patient_State", "TX")),
        "Claim_Status": str(claim_data.get("Claim_Status", "Pending")),
        "Length_of_Stay": int(claim_data.get("Length_of_Stay", 2)),
        "Visit_Type": str(claim_data.get("Visit_Type", "Outpatient")),
        "Chronic_Condition_Flag": int(claim_data.get("Chronic_Condition_Flag", claim_data.get("chronicConditions", 0))),
        "Prior_Visits_12m": int(claim_data.get("Prior_Visits_12m", claim_data.get("priorVisits", 1))),
        "witnesses_count": int(claim_data.get("witnesses_count", 0)),
        "police_report_available": int(claim_data.get("police_report_available", 0))
    }

    # 3. Create DataFrame and run feature engineering
    df = pd.DataFrame([normalized])
    df_engineered = run_feature_engineering(df)

    # 4. Transform features using the ColumnTransformer
    processed = preprocessor.transform(df_engineered)

    # 5. Keras model prediction
    prob = float(model.predict(processed, verbose=0)[0][0])

    # 6. Assign risk level based on probability score
    if prob < 0.30:
        risk_level = "Low"
    elif prob < 0.70:
        risk_level = "Medium"
    else:
        risk_level = "High"

    label = "Fraud" if prob >= 0.50 else "Not Fraud"
    
    # 7. Generate explainability payload passing fully engineered features
    explainability = generate_explainability_report(df_engineered.iloc[0].to_dict(), prob, risk_level)

    # 8. Structure standard contract
    prediction_timestamp = datetime.utcnow().isoformat() + "Z"
    model_version = metadata.get("model_version", "dl_keras_v1.0")

    res = {
        # Structured output for modern dashboard and claim services
        "prediction": {
            "label": label,
            "risk_level": risk_level,
            "fraud_probability": explainability["fraud_probability"],
            "probability": explainability["probability"],
            "confidence": explainability["prediction_confidence"],
            "prediction_timestamp": prediction_timestamp,
            "model_version": model_version
        },
        "explainability": {
            "top_risk_factors": explainability["top_risk_factors"],
            "top_reasons": explainability["top_reasons"],
            "positive_indicators": explainability["positive_indicators"],
            "negative_indicators": explainability["negative_indicators"],
            "feature_importance": explainability["feature_importance"],
            "feature_contributions": explainability["feature_contributions"],
            "reviewer_notes": explainability["reviewer_notes"],
            "recommended_action": explainability["recommended_action"],
            "recommendation": explainability["recommendation"],
            "investigation_advice": explainability["investigation_advice"],
            "human_readable_explanation": explainability["human_readable_explanation"]
        },
        
        # Flat properties for compatibility & exact user requirement alignment
        "probability": explainability["probability"],
        "fraud_probability": explainability["fraud_probability"],
        "risk_level": risk_level,
        "prediction_confidence": explainability["prediction_confidence"],
        "top_reasons": explainability["top_reasons"],
        "top_risk_factors": explainability["top_risk_factors"],
        "feature_contributions": explainability["feature_contributions"],
        "feature_importance": explainability["feature_importance"],
        "recommendation": explainability["recommendation"],
        "recommended_action": explainability["recommended_action"],
        "investigation_advice": explainability["investigation_advice"],
        "human_readable_explanation": explainability["human_readable_explanation"],
        "model_version": model_version,
        "prediction_timestamp": prediction_timestamp,
        "positive_indicators": explainability["positive_indicators"],
        "negative_indicators": explainability["negative_indicators"],
        "reviewer_notes": explainability["reviewer_notes"],
        
        # Old flat keys for direct backward compatibility
        "predicted_label": label,
        "confidence": explainability["prediction_confidence"] / 100.0,
        "reasons": explainability["top_risk_factors"],
        "metadata": metadata
    }

    return res

def get_model_health_status() -> dict:
    """
    Returns loaded model details and health status check.
    """
    model, _, metadata = load_artifacts()
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "model_version": metadata.get("model_version", "dl_keras_v1.0"),
        "backend": "Keras 3 (PyTorch Backend)",
        "metadata": metadata
    }

if __name__ == "__main__":
    print("[TEST v1] Compiling and running self-test claim prediction...")
    test_claim = {
        "age": 52,
        "gender": "Female",
        "diagnosis": "I10",
        "claimAmount": 1200.00,
        "Length_of_Stay": 8,
        "Number_of_Claims_Per_Provider_Monthly": 85,
        "Prior_Visits_12m": 6
    }
    result = predict_claim(test_claim)
    print("=" * 60)
    print("Test Result:")
    for k, v in result.items():
        if k in ["prediction", "explainability"]:
            print(f"  {k}:")
            for sub_k, sub_v in v.items():
                print(f"    {sub_k}: {sub_v}")
        elif not isinstance(v, dict):
            print(f"  {k}: {v}")
    print("=" * 60)
