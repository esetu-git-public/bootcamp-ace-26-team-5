import os
from models import InsurancePolicy
from utils.supabase_client import supabase
from utils.sqlite_client import get_sqlite_conn

def find_policy_by_id(policy_id: int) -> InsurancePolicy:
    """
    Retrieve an insurance policy by its primary key ID.
    """
    if os.getenv("DB_PROVIDER") == "sqlite":
        try:
            with get_sqlite_conn() as conn:
                row = conn.execute("SELECT * FROM insurance_policies WHERE policy_id = ?", (policy_id,)).fetchone()
                if row:
                    return InsurancePolicy.from_dict(dict(row))
        except Exception as e:
            print(f"Error finding SQLite policy by ID: {e}")
        return None

    try:
        res = supabase.table("insurance_policies").select("*").eq("policy_id", policy_id).execute()
        if res.data:
            return InsurancePolicy.from_dict(res.data[0])
    except Exception as e:
        print(f"Error finding policy by ID: {e}")
    return None


def find_policy_by_policyholder_id(policyholder_id: int) -> InsurancePolicy:
    """
    Retrieve an insurance policy by the policyholder's ID.
    """
    if os.getenv("DB_PROVIDER") == "sqlite":
        try:
            with get_sqlite_conn() as conn:
                row = conn.execute("SELECT * FROM insurance_policies WHERE policyholder_id = ?", (policyholder_id,)).fetchone()
                if row:
                    return InsurancePolicy.from_dict(dict(row))
        except Exception as e:
            print(f"Error finding SQLite policy by policyholder ID: {e}")
        return None

    try:
        res = supabase.table("insurance_policies").select("*").eq("policyholder_id", policyholder_id).execute()
        if res.data:
            return InsurancePolicy.from_dict(res.data[0])
    except Exception as e:
        print(f"Error finding policy by policyholder ID: {e}")
    return None


def save_policy(policy: InsurancePolicy) -> InsurancePolicy:
    """
    Save or insert an insurance policy record into database.
    """
    payload = {
        "policy_number": policy.policy_number,
        "policyholder_id": policy.policyholder_id,
        "insurance_type": policy.insurance_type,
        "start_date": policy.start_date.isoformat() if hasattr(policy.start_date, "isoformat") else policy.start_date,
        "end_date": policy.end_date.isoformat() if hasattr(policy.end_date, "isoformat") else policy.end_date,
        "premium_amount": policy.premium_amount,
        "coverage_amount": policy.coverage_amount,
        "policy_status": policy.policy_status
    }
    
    if os.getenv("DB_PROVIDER") == "sqlite":
        try:
            with get_sqlite_conn() as conn:
                cursor = conn.cursor()
                if policy.policy_id:
                    cursor.execute(
                        """UPDATE insurance_policies SET policy_number = ?, policyholder_id = ?, insurance_type = ?, 
                           start_date = ?, end_date = ?, premium_amount = ?, coverage_amount = ?, policy_status = ? 
                           WHERE policy_id = ?""",
                        (payload["policy_number"], payload["policyholder_id"], payload["insurance_type"],
                         payload["start_date"], payload["end_date"], payload["premium_amount"],
                         payload["coverage_amount"], payload["policy_status"], policy.policy_id)
                    )
                else:
                    cursor.execute(
                        """INSERT INTO insurance_policies (policy_number, policyholder_id, insurance_type, 
                           start_date, end_date, premium_amount, coverage_amount, policy_status) 
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                        (payload["policy_number"], payload["policyholder_id"], payload["insurance_type"],
                         payload["start_date"], payload["end_date"], payload["premium_amount"],
                         payload["coverage_amount"], payload["policy_status"])
                    )
                    policy.policy_id = cursor.lastrowid
                conn.commit()
                row = conn.execute("SELECT * FROM insurance_policies WHERE policy_id = ?", (policy.policy_id,)).fetchone()
                if row:
                    return InsurancePolicy.from_dict(dict(row))
        except Exception as e:
            print(f"Error saving SQLite policy: {e}")
        return policy

    try:
        if policy.policy_id:
            res = supabase.table("insurance_policies").update(payload).eq("policy_id", policy.policy_id).execute()
        else:
            res = supabase.table("insurance_policies").insert(payload).execute()
            
        if res.data:
            return InsurancePolicy.from_dict(res.data[0])
    except Exception as e:
        print(f"Error saving policy: {e}")
    return policy
