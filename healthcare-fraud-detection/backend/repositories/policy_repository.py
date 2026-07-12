from models import InsurancePolicy
from utils.supabase_client import supabase

def find_policy_by_id(policy_id: int) -> InsurancePolicy:
    """
    Retrieve an insurance policy by its primary key ID.
    """
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
    try:
        res = supabase.table("insurance_policies").select("*").eq("policyholder_id", policyholder_id).execute()
        if res.data:
            return InsurancePolicy.from_dict(res.data[0])
    except Exception as e:
        print(f"Error finding policy by policyholder ID: {e}")
    return None


def save_policy(policy: InsurancePolicy) -> InsurancePolicy:
    """
    Save or insert an insurance policy record into Supabase.
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
