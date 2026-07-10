from models import Policyholder
from utils.supabase_client import supabase

def find_policyholder_by_id(policyholder_id: int) -> Policyholder:
    """
    Retrieve a policyholder by their primary key ID.
    """
    try:
        res = supabase.table("policyholders").select("*").eq("policyholder_id", policyholder_id).execute()
        if res.data:
            return Policyholder.from_dict(res.data[0])
    except Exception as e:
        print(f"Error finding policyholder by ID: {e}")
    return None


def find_policyholder_by_name(full_name: str) -> Policyholder:
    """
    Retrieve a policyholder by their full name.
    """
    if not full_name:
        return None
    try:
        res = supabase.table("policyholders").select("*").eq("full_name", full_name.strip()).execute()
        if res.data:
            return Policyholder.from_dict(res.data[0])
    except Exception as e:
        print(f"Error finding policyholder by name: {e}")
    return None


def save_policyholder(holder: Policyholder) -> Policyholder:
    """
    Save or insert a policyholder record into Supabase.
    """
    payload = {
        "full_name": holder.full_name,
        "gender": holder.gender,
        "date_of_birth": holder.date_of_birth.isoformat() if hasattr(holder.date_of_birth, "isoformat") else holder.date_of_birth,
        "city": holder.city,
        "state": holder.state
    }
    
    try:
        if holder.policyholder_id:
            res = supabase.table("policyholders").update(payload).eq("policyholder_id", holder.policyholder_id).execute()
        else:
            res = supabase.table("policyholders").insert(payload).execute()
            
        if res.data:
            return Policyholder.from_dict(res.data[0])
    except Exception as e:
        print(f"Error saving policyholder: {e}")
    return holder
