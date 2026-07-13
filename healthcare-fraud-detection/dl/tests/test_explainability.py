import os
import sys

# -------------------------------------------------------
# Add prediction folder to Python path
# -------------------------------------------------------

CURRENT_DIR = os.path.dirname(__file__)
PREDICTION_DIR = os.path.abspath(
    os.path.join(CURRENT_DIR, "..", "prediction")
)

sys.path.insert(0, PREDICTION_DIR)

from explainability import generate_reasons


# -------------------------------------------------------
# Sample Data
# -------------------------------------------------------

high_risk_claim = {
    "Claim_Amount": 850,
    "Prior_Visits_12m": 6,
    "Length_of_Stay": 8,
    "Number_of_Claims_Per_Provider_Monthly": 80
}

low_risk_claim = {
    "Claim_Amount": 200,
    "Prior_Visits_12m": 1,
    "Length_of_Stay": 2,
    "Number_of_Claims_Per_Provider_Monthly": 10
}


# -------------------------------------------------------
# Test 1: High Claim Amount
# -------------------------------------------------------

def test_high_claim_amount():
    reasons = generate_reasons(high_risk_claim)
    assert "High Claim Amount" in reasons


# -------------------------------------------------------
# Test 2: Frequent Previous Visits
# -------------------------------------------------------

def test_frequent_previous_visits():
    reasons = generate_reasons(high_risk_claim)
    assert "Frequent Previous Visits" in reasons


# -------------------------------------------------------
# Test 3: Long Hospital Stay
# -------------------------------------------------------

def test_long_hospital_stay():
    reasons = generate_reasons(high_risk_claim)
    assert "Long Hospital Stay" in reasons


# -------------------------------------------------------
# Test 4: High Provider Claim Volume
# -------------------------------------------------------

def test_high_provider_claim_volume():
    reasons = generate_reasons(high_risk_claim)
    assert "High Provider Claim Volume" in reasons


# -------------------------------------------------------
# Test 5: No Fraud Indicators
# -------------------------------------------------------

def test_no_fraud_indicators():
    reasons = generate_reasons(low_risk_claim)

    assert reasons == [
        "No significant fraud indicators detected."
    ]


# -------------------------------------------------------
# Test 6: Return Type
# -------------------------------------------------------

def test_return_type():
    reasons = generate_reasons(high_risk_claim)

    assert isinstance(reasons, list)


# -------------------------------------------------------
# Test 7: At Least One Reason
# -------------------------------------------------------

def test_reason_not_empty():
    reasons = generate_reasons(high_risk_claim)

    assert len(reasons) > 0