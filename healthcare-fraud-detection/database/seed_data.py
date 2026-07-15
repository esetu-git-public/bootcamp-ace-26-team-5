import sqlite3
from pathlib import Path

db_path = Path(__file__).resolve().parent / "claims.db"

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

import bcrypt

# Generate secure password hashes
salt = bcrypt.gensalt()
admin_hash = bcrypt.hashpw(b"admin123", salt).decode("utf-8")
officer_hash = bcrypt.hashpw(b"officer123", salt).decode("utf-8")

# Users
cursor.executemany("""
    INSERT INTO users (full_name, email, password_hash, role)
    VALUES (?, ?, ?, ?)
""", [
    ("Admin User", "admin@fraudshield.com", admin_hash, "admin"),
    ("Claims Officer", "officer@fraudshield.com", officer_hash, "employee")
])

# Policyholders
cursor.executemany("""
    INSERT INTO policyholders
    (full_name, date_of_birth, gender, phone, email, address, city, state)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""", [
    ("Ravi Kumar", "1990-05-15", "Male", "9876543210", "ravi@email.com",
     "Madhapur", "Hyderabad", "Telangana"),

    ("Anjali Reddy", "1988-10-22", "Female", "9123456780", "anjali@email.com",
     "Kukatpally", "Hyderabad", "Telangana"),

    ("Suresh Naidu", "1995-03-09", "Male", "9988776655", "suresh@email.com",
     "Gachibowli", "Hyderabad", "Telangana")
])

# Policies
cursor.executemany("""
    INSERT INTO insurance_policies
    (policy_number, policyholder_id, insurance_type, start_date, end_date,
     premium_amount, coverage_amount, policy_status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""", [
    ("POL-1001", 1, "Vehicle", "2025-01-01", "2026-01-01", 12000, 500000, "active"),
    ("POL-1002", 2, "Health", "2025-06-01", "2026-06-01", 18000, 1000000, "active"),
    ("POL-1003", 3, "Vehicle", "2025-03-01", "2026-03-01", 15000, 700000, "active")
])

# Claims
cursor.executemany("""
    INSERT INTO insurance_claims
    (claim_number, policy_id, claim_date, incident_date, claim_type,
     claim_amount, incident_location, incident_description,
     police_report_available, witnesses_count, claim_status, submitted_by)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", [
    ("CLM-5001", 1, "2025-08-10", "2025-08-08", "Accident",
     85000, "Hyderabad", "Vehicle collision near junction",
     1, 2, "submitted", 2),

    ("CLM-5002", 2, "2025-08-12", "2025-08-11", "Medical",
     350000, "Hyderabad", "Emergency hospital treatment",
     0, 0, "submitted", 2),

    ("CLM-5003", 3, "2025-09-05", "2025-09-03", "Theft",
     520000, "Hyderabad", "Vehicle reported stolen at night",
     0, 0, "under_review", 2)
])

# Predictions now correctly match claim IDs 1, 2, and 3
cursor.executemany("""
    INSERT INTO fraud_predictions
    (claim_id, predicted_label, fraud_probability, risk_level,
     model_version, remarks)
    VALUES (?, ?, ?, ?, ?, ?)
""", [
    (1, "Not Fraud", 0.12, "Low", "v1.0", "Police report and witnesses available"),
    (2, "Fraud", 0.78, "High", "v1.0", "High claim amount with limited supporting evidence"),
    (3, "Fraud", 0.91, "High", "v1.0", "High-value theft claim with no police report")
])

connection.commit()
connection.close()

print("Sample data inserted successfully.")