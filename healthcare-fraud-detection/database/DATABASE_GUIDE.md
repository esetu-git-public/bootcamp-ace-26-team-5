# Database Guide — Insurance Claim Fraud Detection

## Database Used

This project uses SQLite.

Database file:

```text
database/claims.db
```

SQLite is used because it is lightweight, works directly with Python, and does not require a separate database server.

---

## Database Folder Structure

```text
database/
├── __init__.py
├── claims.db
├── schema.sql
├── init_db.py
├── seed_data.py
├── db_connection.py
├── claim_repository.py
├── check_db.py
└── view_claims.py
```

---

## Main Tables

| Table | Purpose |
|---|---|
| `users` | Stores admins and claims officers |
| `policyholders` | Stores insurance customer details |
| `insurance_policies` | Stores insurance policy information |
| `insurance_claims` | Stores submitted insurance claims |
| `fraud_predictions` | Stores fraud prediction results from the ML model |

---

## Database Relationships

```text
Policyholder
    ↓
Insurance Policy
    ↓
Insurance Claim
    ↓
Fraud Prediction
```

A policyholder can have multiple insurance policies.

A policy can have multiple claims.

A claim has one current fraud prediction. If the ML model runs again, the existing prediction is updated.

---

## Database Setup

Run these commands from the project root:

```bash
python database/init_db.py
```

This creates all required tables inside:

```text
database/claims.db
```

---

## Optional Demo Data

To insert sample customers, policies, claims, and predictions:

```bash
python database/seed_data.py
```

Warning: `seed_data.py` clears existing database records and inserts demo records again. Use it only for testing or demonstrations.

To view demo data:

```bash
python database/view_claims.py
```

---

## Database Connection

Use this function whenever backend or ML code needs database access:

```python
from database.db_connection import get_db_connection

connection = get_db_connection()
cursor = connection.cursor()

cursor.execute("SELECT * FROM insurance_claims")
claims = cursor.fetchall()

connection.close()
```

---

## Import Main Database Functions

```python
from database.claim_repository import (
    add_policyholder,
    add_policy,
    add_claim,
    save_prediction,
    get_claim_by_id,
    get_all_claims_with_predictions,
    update_claim_status
)
```

---

## 1. Add Policyholder

```python
policyholder_id = add_policyholder(
    full_name="Priya Sharma",
    date_of_birth="1994-07-18",
    gender="Female",
    phone="9012345678",
    email="priya.sharma@email.com",
    address="Banjara Hills",
    city="Hyderabad",
    state="Telangana"
)
```

This returns the newly created `policyholder_id`.

---

## 2. Add Insurance Policy

```python
policy_id = add_policy(
    policy_number="POL-3001",
    policyholder_id=policyholder_id,
    insurance_type="Vehicle",
    start_date="2026-01-01",
    end_date="2027-01-01",
    premium_amount=15000,
    coverage_amount=700000
)
```

This returns the newly created `policy_id`.

---

## 3. Add Insurance Claim

This function should be called when the frontend submits a new insurance claim form.

```python
claim_id = add_claim(
    claim_number="CLM-7001",
    policy_id=policy_id,
    claim_date="2026-07-04",
    incident_date="2026-07-03",
    claim_type="Accident",
    claim_amount=200000,
    incident_location="Hyderabad",
    incident_description="Vehicle accident near junction",
    police_report_available=1,
    witnesses_count=2,
    submitted_by=2
)
```

This returns the newly created `claim_id`.

---

## 4. Save ML Fraud Prediction

After the ML model predicts whether a claim is fraud or not fraud:

```python
prediction_id = save_prediction(
    claim_id=claim_id,
    predicted_label="Fraud",
    fraud_probability=0.84,
    risk_level="High",
    model_version="v1.0",
    remarks="High claim amount compared with policy premium"
)
```

Allowed prediction labels:

```text
Fraud
Not Fraud
```

Allowed risk levels:

```text
Low
Medium
High
```

---

## 5. Fetch One Complete Claim for ML Model

The ML module can fetch claim, policy, and customer details together:

```python
claim = get_claim_by_id(claim_id)

print(claim)
```

Example returned data:

```python
{
    "claim_id": 4,
    "claim_number": "CLM-6001",
    "claim_amount": 220000.0,
    "police_report_available": 1,
    "witnesses_count": 1,
    "premium_amount": 14000.0,
    "coverage_amount": 650000.0,
    "insurance_type": "Vehicle",
    "policyholder_name": "Priya Sharma",
    "city": "Hyderabad"
}
```

---

## 6. Fetch Dashboard Data

The frontend/backend can fetch all claims with their latest fraud prediction data:

```python
claims = get_all_claims_with_predictions()

for claim in claims:
    print(claim)
```

This returns a list of dictionaries containing:

```text
Claim Number
Customer Name
Claim Amount
Claim Status
Insurance Type
Prediction Label
Fraud Probability
Risk Level
Model Version
Prediction Date
Remarks
```

---

## 7. Update Claim Status

Allowed claim statuses:

```text
submitted
under_review
approved
rejected
```

Example:

```python
update_claim_status(claim_id, "under_review")
```

Later, an employee/admin can update it:

```python
update_claim_status(claim_id, "approved")
```

or:

```python
update_claim_status(claim_id, "rejected")
```

---

## Complete Workflow

```text
Frontend submits customer details
        ↓
add_policyholder()
        ↓
add_policy()
        ↓
add_claim()
        ↓
ML model reads claim using get_claim_by_id()
        ↓
ML model predicts fraud probability
        ↓
save_prediction()
        ↓
Frontend dashboard uses get_all_claims_with_predictions()
        ↓
Employee updates status using update_claim_status()
```

---

## Testing Files

These files are only for testing the database module:

```text
test_claim_flow.py
test_get_claim.py
test_dashboard_data.py
test_update_status.py
```

Run them from the project root:

```bash
python test_claim_flow.py
python test_get_claim.py
python test_dashboard_data.py
python test_update_status.py
```

---

## Important Notes for Team Members

- Run `python database/init_db.py` once before starting the project.
- Use `seed_data.py` only when demo data is needed.
- Do not manually edit `claims.db`.
- Use functions from `database/claim_repository.py` for all database operations.
- Always close database connections after use.
- `claims.db` should not be pushed to GitHub because it may contain local testing data.