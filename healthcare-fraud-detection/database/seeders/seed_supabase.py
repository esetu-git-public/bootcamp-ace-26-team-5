import sys
import os
import bcrypt
from datetime import datetime, date, timedelta

# Add parent and backend directories to path for imports
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")

if BACKEND_DIR not in sys.path:
    sys.path.append(BACKEND_DIR)

from utils.supabase_client import supabase

def seed_supabase():
    print("[SEEDER] Connecting to Supabase and purging old data...")
    
    # Delete child tables first, then parent tables
    try:
        supabase.table("notifications").delete().neq("notification_id", -1).execute()
        supabase.table("fraud_predictions").delete().neq("prediction_id", -1).execute()
        supabase.table("audit_logs").delete().neq("log_id", -1).execute()
        supabase.table("insurance_claims").delete().neq("claim_id", -1).execute()
        supabase.table("insurance_policies").delete().neq("policy_id", -1).execute()
        supabase.table("policyholders").delete().neq("policyholder_id", -1).execute()
        supabase.table("users").delete().neq("user_id", -1).execute()
        print("[SEEDER] Database tables purged successfully.")
    except Exception as e:
        print(f"[SEEDER] Warning: Failed to purge database tables: {e}")
        # Proceed anyway as some tables might already be empty or missing RLS permissions
        
    print("[SEEDER] Generating secure password hashes...")
    salt = bcrypt.gensalt()
    admin_hash = bcrypt.hashpw(b"admin123", salt).decode("utf-8")
    officer_hash = bcrypt.hashpw(b"officer123", salt).decode("utf-8")
    
    # 1. Create Users
    print("[SEEDER] Inserting Users...")
    users_data = [
        {"full_name": "Admin User", "email": "admin@fraudshield.com", "password_hash": admin_hash, "role": "admin"},
        {"full_name": "Claims Officer", "email": "officer@fraudshield.com", "password_hash": officer_hash, "role": "employee"}
    ]
    user_ids = {}
    for user in users_data:
        res = supabase.table("users").insert(user).execute()
        if res.data:
            inserted = res.data[0]
            user_ids[inserted["email"]] = inserted["user_id"]
            print(f" - Created user: {inserted['email']} (ID: {inserted['user_id']})")
            
    officer_id = user_ids.get("officer@fraudshield.com")
    
    # 2. Create Policyholders
    print("[SEEDER] Inserting Policyholders...")
    policyholders_data = [
        {
            "full_name": "Ravi Kumar",
            "date_of_birth": "1990-05-15",
            "gender": "Male",
            "phone": "9876543210",
            "email": "ravi@email.com",
            "address": "Madhapur",
            "city": "Hyderabad",
            "state": "Telangana"
        },
        {
            "full_name": "Anjali Reddy",
            "date_of_birth": "1988-10-22",
            "gender": "Female",
            "phone": "9123456780",
            "email": "anjali@email.com",
            "address": "Kukatpally",
            "city": "Hyderabad",
            "state": "Telangana"
        },
        {
            "full_name": "Suresh Naidu",
            "date_of_birth": "1995-03-09",
            "gender": "Male",
            "phone": "9988776655",
            "email": "suresh@email.com",
            "address": "Gachibowli",
            "city": "Hyderabad",
            "state": "Telangana"
        }
    ]
    holder_ids = {}
    for holder in policyholders_data:
        res = supabase.table("policyholders").insert(holder).execute()
        if res.data:
            inserted = res.data[0]
            holder_ids[inserted["full_name"]] = inserted["policyholder_id"]
            print(f" - Created policyholder: {inserted['full_name']} (ID: {inserted['policyholder_id']})")
            
    # 3. Create Policies
    print("[SEEDER] Inserting Policies...")
    policies_data = [
        {
            "policy_number": "POL-1001",
            "policyholder_id": holder_ids["Ravi Kumar"],
            "insurance_type": "Vehicle",
            "start_date": "2025-01-01",
            "end_date": "2026-01-01",
            "premium_amount": 12000.0,
            "coverage_amount": 500000.0,
            "policy_status": "active"
        },
        {
            "policy_number": "POL-1002",
            "policyholder_id": holder_ids["Anjali Reddy"],
            "insurance_type": "Health",
            "start_date": "2025-06-01",
            "end_date": "2026-06-01",
            "premium_amount": 18000.0,
            "coverage_amount": 1000000.0,
            "policy_status": "active"
        },
        {
            "policy_number": "POL-1003",
            "policyholder_id": holder_ids["Suresh Naidu"],
            "insurance_type": "Vehicle",
            "start_date": "2025-03-01",
            "end_date": "2026-03-01",
            "premium_amount": 15000.0,
            "coverage_amount": 700000.0,
            "policy_status": "active"
        }
    ]
    policy_ids = {}
    for policy in policies_data:
        res = supabase.table("insurance_policies").insert(policy).execute()
        if res.data:
            inserted = res.data[0]
            policy_ids[inserted["policy_number"]] = inserted["policy_id"]
            print(f" - Created policy: {inserted['policy_number']} (ID: {inserted['policy_id']})")
            
    # 4. Create Claims
    print("[SEEDER] Inserting Claims...")
    claims_data = [
        {
            "claim_number": "CLM-5001",
            "policy_id": policy_ids["POL-1001"],
            "claim_date": "2025-08-10",
            "incident_date": "2025-08-08",
            "claim_type": "Accident",
            "claim_amount": 85000.00,
            "incident_location": "Hyderabad",
            "incident_description": "Vehicle collision near junction",
            "police_report_available": 1,
            "witnesses_count": 2,
            "claim_status": "approved",
            "submitted_by": officer_id
        },
        {
            "claim_number": "CLM-5002",
            "policy_id": policy_ids["POL-1002"],
            "claim_date": "2025-08-12",
            "incident_date": "2025-08-11",
            "claim_type": "Medical",
            "claim_amount": 350000.00,
            "incident_location": "Hyderabad",
            "incident_description": "Emergency hospital treatment",
            "police_report_available": 0,
            "witnesses_count": 0,
            "claim_status": "under_review",
            "submitted_by": officer_id
        },
        {
            "claim_number": "CLM-5003",
            "policy_id": policy_ids["POL-1003"],
            "claim_date": "2025-09-05",
            "incident_date": "2025-09-03",
            "claim_type": "Theft",
            "claim_amount": 520000.00,
            "incident_location": "Hyderabad",
            "incident_description": "Vehicle reported stolen at night",
            "police_report_available": 0,
            "witnesses_count": 0,
            "claim_status": "under_review",
            "submitted_by": officer_id
        }
    ]
    claim_ids = {}
    for claim in claims_data:
        res = supabase.table("insurance_claims").insert(claim).execute()
        if res.data:
            inserted = res.data[0]
            claim_ids[inserted["claim_number"]] = inserted["claim_id"]
            print(f" - Created claim: {inserted['claim_number']} (ID: {inserted['claim_id']})")
            
    # 5. Create Predictions
    print("[SEEDER] Inserting Predictions...")
    predictions_data = [
        {
            "claim_id": claim_ids["CLM-5001"],
            "predicted_label": "Not Fraud",
            "fraud_probability": 0.12,
            "risk_level": "Low",
            "model_version": "dl_keras_v1.0",
            "remarks": "The claim was successfully evaluated as Low Risk (12.0% probability). No major billing anomalies detected."
        },
        {
            "claim_id": claim_ids["CLM-5002"],
            "predicted_label": "Fraud",
            "fraud_probability": 0.78,
            "risk_level": "High",
            "model_version": "dl_keras_v1.0",
            "remarks": "High Risk Alert (78.0% probability). The claim demonstrates high billing frequency, abnormal stay duration, or large claim size."
        },
        {
            "claim_id": claim_ids["CLM-5003"],
            "predicted_label": "Fraud",
            "fraud_probability": 0.91,
            "risk_level": "High",
            "model_version": "dl_keras_v1.0",
            "remarks": "High Risk Alert (91.0% probability). The claim demonstrates high billing frequency, abnormal stay duration, or large claim size."
        }
    ]
    for pred in predictions_data:
        res = supabase.table("fraud_predictions").insert(pred).execute()
        if res.data:
            inserted = res.data[0]
            print(f" - Created prediction for Claim ID: {inserted['claim_id']} (ID: {inserted['prediction_id']})")
            
    print("[SEEDER] Supabase data seeding completed successfully!")

if __name__ == "__main__":
    seed_supabase()
