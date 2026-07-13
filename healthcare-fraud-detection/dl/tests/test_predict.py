import os
import sys
import numpy as np
import pandas as pd
from unittest.mock import MagicMock

# -------------------------------------------------------
# Add dl folder to Python path
# -------------------------------------------------------

CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))

sys.path.insert(0, PROJECT_ROOT)

# Import as package
from prediction import predict


# -------------------------------------------------------
# Mock model and preprocessor
# -------------------------------------------------------

predict.model = MagicMock()
predict.preprocessor = MagicMock()

predict.preprocessor.transform.return_value = np.array([[1, 2, 3]])
predict.model.predict.return_value = np.array([[0.85]])


# -------------------------------------------------------
# Sample Claim
# -------------------------------------------------------

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
    "Prior_Visits_12m": 6,
}


# -------------------------------------------------------
# Feature Engineering Test
# -------------------------------------------------------

def test_feature_engineering():
    df = pd.DataFrame([sample_claim])

    result = predict.feature_engineering(df)

    assert "Approval_Ratio" in result.columns
    assert "Risk_Score" in result.columns
    assert result["High_Claim"].iloc[0] == 1
    assert result["Long_Stay"].iloc[0] == 1
    assert result["Frequent_Visitor"].iloc[0] == 1


# -------------------------------------------------------
# Prediction Output Type
# -------------------------------------------------------

def test_predict_returns_dictionary():
    result = predict.predict_claim(sample_claim)

    assert isinstance(result, dict)


# -------------------------------------------------------
# Prediction Label
# -------------------------------------------------------

def test_prediction_label():
    result = predict.predict_claim(sample_claim)

    assert result["prediction"] == "Fraud"


# -------------------------------------------------------
# Fraud Probability
# -------------------------------------------------------

def test_probability_range():
    result = predict.predict_claim(sample_claim)

    assert 0 <= result["fraud_probability"] <= 100


# -------------------------------------------------------
# Confidence
# -------------------------------------------------------

def test_confidence_range():
    result = predict.predict_claim(sample_claim)

    assert 0 <= result["confidence"] <= 100


# -------------------------------------------------------
# Risk Level
# -------------------------------------------------------

def test_risk_level():
    result = predict.predict_claim(sample_claim)

    assert result["risk_level"] == "High"


# -------------------------------------------------------
# Reasons
# -------------------------------------------------------

def test_reasons_exist():
    result = predict.predict_claim(sample_claim)

    assert isinstance(result["reasons"], list)
    assert len(result["reasons"]) > 0


# -------------------------------------------------------
# Model Version
# -------------------------------------------------------

def test_model_version():
    result = predict.predict_claim(sample_claim)

    assert result["model_version"] == "TensorFlow-Keras-v1"