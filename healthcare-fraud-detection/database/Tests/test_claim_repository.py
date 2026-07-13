import pytest

from database.claim_repository import (
    add_policyholder,
    add_policy,
    add_claim,
    save_prediction,
    get_claim_by_id,
    get_all_claims_with_predictions,
    update_claim_status,
)


# -------------------------------
# Helper Fixture
# -------------------------------

@pytest.fixture
def sample_data():

    holder_id = add_policyholder(
        full_name="John Doe",
        date_of_birth="1990-01-01",
        gender="Male",
        phone="9876543210",
        email="john@example.com",
        address="123 Main Street",
        city="Hyderabad",
        state="Telangana"
    )

    policy_id = add_policy(
        policy_number="POL1001",
        policyholder_id=holder_id,
        insurance_type="Health",
        start_date="2025-01-01",
        end_date="2026-01-01",
        premium_amount=15000,
        coverage_amount=500000
    )

    return holder_id, policy_id


# ===================================================
# add_policyholder()
# ===================================================

def test_add_policyholder_success():

    holder_id = add_policyholder(
        "Alice",
        "1995-05-10",
        "Female",
        "9999999999",
        "alice@example.com",
        "Street 1",
        "Bangalore",
        "Karnataka"
    )

    assert holder_id is not None
    assert holder_id > 0


# ===================================================
# add_policy()
# ===================================================

def test_add_policy_success(sample_data):

    holder_id, _ = sample_data

    policy_id = add_policy(
        "POL999",
        holder_id,
        "Health",
        "2025-01-01",
        "2026-01-01",
        25000,
        1000000
    )

    assert policy_id is not None


# ===================================================
# add_claim()
# ===================================================

def test_add_claim_success(sample_data):

    _, policy_id = sample_data

    claim_id = add_claim(
        claim_number="CLM001",
        policy_id=policy_id,
        claim_date="2025-06-01",
        incident_date="2025-05-30",
        claim_type="Hospitalization",
        claim_amount=50000,
        incident_location="Hyderabad",
        incident_description="Accident",
        police_report_available=1,
        witnesses_count=2
    )

    assert claim_id > 0


def test_add_claim_without_claim_number(sample_data):

    _, policy_id = sample_data

    with pytest.raises(ValueError):

        add_claim(
            "",
            policy_id,
            "2025-06-01",
            "2025-05-30",
            "Hospitalization",
            50000,
            "Hyderabad",
            "Accident",
            1,
            2
        )


def test_add_claim_negative_amount(sample_data):

    _, policy_id = sample_data

    with pytest.raises(ValueError):

        add_claim(
            "CLM002",
            policy_id,
            "2025-06-01",
            "2025-05-30",
            "Hospitalization",
            -500,
            "Hyderabad",
            "Accident",
            1,
            2
        )


def test_add_claim_negative_witness(sample_data):

    _, policy_id = sample_data

    with pytest.raises(ValueError):

        add_claim(
            "CLM003",
            policy_id,
            "2025-06-01",
            "2025-05-30",
            "Hospitalization",
            50000,
            "Hyderabad",
            "Accident",
            1,
            -1
        )


def test_invalid_police_report(sample_data):

    _, policy_id = sample_data

    with pytest.raises(ValueError):

        add_claim(
            "CLM004",
            policy_id,
            "2025-06-01",
            "2025-05-30",
            "Hospitalization",
            50000,
            "Hyderabad",
            "Accident",
            5,
            1
        )


# ===================================================
# save_prediction()
# ===================================================

def test_save_prediction_success(sample_data):

    _, policy_id = sample_data

    claim_id = add_claim(
        "CLM100",
        policy_id,
        "2025-06-01",
        "2025-05-30",
        "Hospitalization",
        100000,
        "Hyderabad",
        "Accident",
        1,
        2
    )

    prediction_id = save_prediction(
        claim_id,
        "Fraud",
        0.95,
        "High"
    )

    assert prediction_id > 0


def test_invalid_prediction_label():

    with pytest.raises(ValueError):

        save_prediction(
            1,
            "Fake",
            0.8,
            "High"
        )


def test_invalid_probability():

    with pytest.raises(ValueError):

        save_prediction(
            1,
            "Fraud",
            2.5,
            "High"
        )


def test_invalid_risk_level():

    with pytest.raises(ValueError):

        save_prediction(
            1,
            "Fraud",
            0.8,
            "Critical"
        )


# ===================================================
# get_claim_by_id()
# ===================================================

def test_get_claim(sample_data):

    _, policy_id = sample_data

    claim_id = add_claim(
        "CLM500",
        policy_id,
        "2025-06-01",
        "2025-05-30",
        "Hospitalization",
        10000,
        "Hyderabad",
        "Description",
        1,
        1
    )

    claim = get_claim_by_id(claim_id)

    assert claim is not None
    assert claim["claim_number"] == "CLM500"


def test_get_invalid_claim():

    claim = get_claim_by_id(999999)

    assert claim is None


# ===================================================
# get_all_claims_with_predictions()
# ===================================================

def test_get_all_claims():

    claims = get_all_claims_with_predictions()

    assert isinstance(claims, list)


# ===================================================
# update_claim_status()
# ===================================================

def test_update_claim_status(sample_data):

    _, policy_id = sample_data

    claim_id = add_claim(
        "CLM700",
        policy_id,
        "2025-06-01",
        "2025-05-30",
        "Hospitalization",
        25000,
        "Hyderabad",
        "Description",
        1,
        1
    )

    result = update_claim_status(
        claim_id,
        "approved"
    )

    assert result is True


def test_invalid_status():

    with pytest.raises(ValueError):

        update_claim_status(
            1,
            "completed"
        )