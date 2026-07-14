import pandas as pd
import numpy as np
from datetime import datetime

from ml.inference.model_loader import load_artifacts, get_model, get_preprocessor, get_metadata
from ml.inference.feature_engineering import run_feature_engineering
from ml.inference.explainability import generate_explainability_report

def predict_claim(claim_data: dict, explain_level: str = "simple") -> dict:
    """
    Orchestrates the Keras Deep Learning prediction flow:
    Raw claim data -> Key normalization -> Feature engineering -> Transformation -> Keras model scoring -> Explainability report.
    """
    # 1. Ensure model and preprocessor are loaded
    model, preprocessor, metadata = load_artifacts()

    # 2. Normalize input keys and map default fallback values
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
        "Chronic_Condition_Flag": int(claim_data.get("Chronic_Condition_Flag", 0)),
        "Prior_Visits_12m": int(claim_data.get("Prior_Visits_12m", 1)),
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
    
    # 7. Generate explainability payload
    explainability = generate_explainability_report(normalized, prob, risk_level)

    # 8. Structure standard contract (combining API backward compatibility)
    res = {
        "fraud_probability": explainability["fraud_probability"],
        "risk_level": explainability["risk_level"],
        "prediction_confidence": explainability["prediction_confidence"],
        "top_risk_factors": explainability["top_risk_factors"],
        "feature_importance": explainability["feature_importance"],
        "positive_indicators": explainability["positive_indicators"],
        "negative_indicators": explainability["negative_indicators"],
        "recommended_action": explainability["recommended_action"],
        "reviewer_notes": explainability["reviewer_notes"],
        
        # Keep old fields for backward compatibility
        "predicted_label": label,
        "confidence": explainability["prediction_confidence"] / 100.0,
        "reasons": explainability["top_risk_factors"],
        "model_version": metadata.get("model_version", "dl_keras_v1.0"),
        "metadata": metadata,

        # Nested keys used by the original backend code
        "prediction": {
            "risk_score": round(prob, 4),
            "risk_level": risk_level,
            "confidence": round(explainability["prediction_confidence"] / 100.0, 4)
        },
        "explainability": {
            "top_risk_factors": explainability["top_risk_factors"],
            "feature_importance": explainability["feature_importance"],
            "positive_indicators": explainability["positive_indicators"],
            "negative_indicators": explainability["negative_indicators"],
            "suggested_action": explainability["recommended_action"],
            "reviewer_notes": explainability["reviewer_notes"]
        }
    }

    return res

def get_model_health_status() -> dict:
    """
    Returns loaded model details and health status check.
    """
    model, _, metadata = load_artifacts()
    return {
        "model_loaded": model is not None,
        "model_version": metadata.get("model_version", "dl_keras_v1.0"),
        "backend": "Keras 3 (PyTorch Backend)",
        "status": "healthy",
        "metadata": metadata
    }

if __name__ == "__main__":
    print("[TEST] Compiling and running self-test claim prediction...")
    test_payload = {
        "age": 52,
        "gender": "Female",
        "diagnosis": "I10",
        "claimAmount": 1200.00,
        "Length_of_Stay": 8,
        "Number_of_Claims_Per_Provider_Monthly": 85,
        "Prior_Visits_12m": 6
    }
    res = predict_claim(test_payload)
    print("=" * 60)
    print("Test Result:")
    for k, v in res.items():
        if k != "metadata":
            print(f"  {k}: {v}")
    print("=" * 60)
