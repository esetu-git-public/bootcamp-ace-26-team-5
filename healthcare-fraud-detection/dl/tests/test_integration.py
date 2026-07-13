import os
import sys

CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))

# Add dl folder to path
sys.path.insert(0, PROJECT_ROOT)

from prediction.predict import predict_claim


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


def test_complete_prediction_pipeline():
    result = predict_claim(sample_claim)

    assert isinstance(result, dict)

    assert "prediction" in result
    assert "fraud_probability" in result
    assert "confidence" in result
    assert "risk_level" in result
    assert "reasons" in result
    assert "model_version" in result

    assert result["prediction"] in ["Fraud", "Not Fraud"]
    assert 0 <= result["fraud_probability"] <= 100
    assert 0 <= result["confidence"] <= 100
    assert result["risk_level"] in ["Low", "Medium", "High"]
    assert isinstance(result["reasons"], list)