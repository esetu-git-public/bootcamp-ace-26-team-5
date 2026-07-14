import sqlite3
from pathlib import Path

db_path = Path(__file__).resolve().parent / "claims.db"

connection = sqlite3.connect(db_path)
cursor = connection.cursor()

cursor.execute("""
    SELECT
        c.claim_number,
        ph.full_name AS policyholder_name,
        p.insurance_type,
        c.claim_type,
        c.claim_amount,
        fp.predicted_label,
        fp.fraud_probability,
        fp.risk_level
    FROM insurance_claims c
    JOIN insurance_policies p ON c.policy_id = p.policy_id
    JOIN policyholders ph ON p.policyholder_id = ph.policyholder_id
    LEFT JOIN fraud_predictions fp ON c.claim_id = fp.claim_id
    ORDER BY c.claim_id;
""")

rows = cursor.fetchall()

print("\nInsurance Claim Fraud Dashboard Data\n")
for row in rows:
    print(
        f"Claim: {row[0]} | Customer: {row[1]} | "
        f"Type: {row[2]} | Amount: ₹{row[4]:,.0f} | "
        f"Prediction: {row[5]} | Fraud Probability: {row[6]} | Risk: {row[7]}"
    )

connection.close()