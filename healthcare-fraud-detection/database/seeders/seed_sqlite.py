import sqlite3
from pathlib import Path
import bcrypt

db_path = Path(__file__).resolve().parent.parent / "claims.db"

connection = sqlite3.connect(db_path)
connection.execute("PRAGMA foreign_keys = ON")
cursor = connection.cursor()

# Delete child tables first, then parent tables
cursor.execute("DELETE FROM model_feedback")
cursor.execute("DELETE FROM fraud_predictions")
cursor.execute("DELETE FROM insurance_claims")
cursor.execute("DELETE FROM insurance_policies")
cursor.execute("DELETE FROM policyholders")
cursor.execute("DELETE FROM users")

# Reset SQLite auto-increment IDs so new records start again from 1
cursor.execute("""
    DELETE FROM sqlite_sequence
    WHERE name IN (
        'model_feedback',
        'fraud_predictions',
        'insurance_claims',
        'insurance_policies',
        'policyholders',
        'users'
    )
""")

# Generate secure password hashes
salt = bcrypt.gensalt()
demo_hash = bcrypt.hashpw(b"demo1234", salt).decode("utf-8")

# Users: Aligned with frontend login credentials
cursor.executemany("""
    INSERT INTO users (full_name, email, password_hash, role)
    VALUES (?, ?, ?, ?)
""", [
    ("Anjali Rao", "admin@claimguard.ai", demo_hash, "admin"),
    ("Priya Sharma", "officer@claimguard.ai", demo_hash, "employee"),
    ("Ava Thompson", "patient@claimguard.ai", demo_hash, "customer")
])

# Policyholders: 3 Policyholders (Ravi, Anjali, Ava)
cursor.executemany("""
    INSERT INTO policyholders
    (full_name, date_of_birth, gender, phone, email, address, city, state)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""", [
    ("Ravi Kumar", "1990-05-15", "Male", "9876543210", "ravi@email.com",
     "Madhapur", "Hyderabad", "Telangana"),
    ("Anjali Reddy", "1988-10-22", "Female", "9123456780", "anjali@email.com",
     "Kukatpally", "Hyderabad", "Telangana"),
    ("Ava Thompson", "1981-07-15", "Female", "9988776655", "patient@claimguard.ai",
     "Gachibowli", "Hyderabad", "Telangana")
])

# Policies: POL-1001, POL-1002, and the customer POL-MOCK-1234
cursor.executemany("""
    INSERT INTO insurance_policies
    (policy_number, policyholder_id, insurance_type, start_date, end_date,
     premium_amount, coverage_amount, policy_status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""", [
    ("POL-1001", 1, "Vehicle", "2025-01-01", "2026-01-01", 12000, 500000, "active"),
    ("POL-1002", 2, "Health", "2025-06-01", "2026-06-01", 18000, 1000000, "active"),
    ("POL-MOCK-1234", 3, "Private Health", "2025-06-01", "2026-06-01", 15000, 700000, "active")
])

# Claims: Seed two initial system claims and one historical claim for Ava Thompson
cursor.executemany("""
    INSERT INTO insurance_claims
    (claim_number, policy_id, claim_date, incident_date, claim_type,
     claim_amount, incident_location, incident_description,
     police_report_available, witnesses_count, claim_status, submitted_by,
     diagnosis_code, procedure_code, provider_name, length_of_stay, visit_type)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", [
    ("CLM-5001", 1, "2025-08-10", "2025-08-08", "Vehicle",
     85000, "Hyderabad", "Vehicle collision near junction",
     1, 2, "approved", 2, "S06", "99213", "Apollo Hospital", 1, "Inpatient"),
     
    ("CLM-5002", 2, "2025-08-12", "2025-08-11", "Medical",
     350000, "Hyderabad", "Emergency hospital treatment",
     0, 0, "under_review", 2, "E11", "99214", "Sunrise General Hospital", 5, "Inpatient"),
     
    ("CLM-5004", 3, "2026-07-10", "2026-07-09", "Medical",
     150, "Hyderabad", "Routine clinical consultation",
     0, 0, "approved", 3, "I10", "99213", "MedCore Clinic", 0, "Outpatient")
])

# Predictions:
cursor.executemany("""
    INSERT INTO fraud_predictions
    (claim_id, predicted_label, fraud_probability, risk_level,
     model_version, remarks)
    VALUES (?, ?, ?, ?, ?, ?)
""", [
    (1, "Not Fraud", 0.12, "Low", "v1.0", "Police report and witnesses available"),
    (2, "Fraud", 0.78, "High", "v1.0", "High claim amount with limited supporting evidence"),
    (3, "Not Fraud", 0.05, "Low", "v1.0", "Routine consultation within normal claim volume")
])

connection.commit()
connection.close()

print("Sample data inserted successfully.")