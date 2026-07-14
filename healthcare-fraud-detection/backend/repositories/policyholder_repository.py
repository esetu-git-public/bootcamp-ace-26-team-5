import os
from models import Policyholder
from utils.supabase_client import supabase
from utils.sqlite_client import get_sqlite_conn

def find_policyholder_by_id(policyholder_id: int) -> Policyholder:
    """
    Retrieve a policyholder by their primary key ID.
    """
    if os.getenv("DB_PROVIDER") == "sqlite":
        try:
            with get_sqlite_conn() as conn:
                row = conn.execute("SELECT * FROM policyholders WHERE policyholder_id = ?", (policyholder_id,)).fetchone()
                if row:
                    return Policyholder.from_dict(dict(row))
        except Exception as e:
            print(f"Error finding SQLite policyholder by ID: {e}")
        return None

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
    if os.getenv("DB_PROVIDER") == "sqlite":
        try:
            with get_sqlite_conn() as conn:
                row = conn.execute("SELECT * FROM policyholders WHERE full_name = ?", (full_name.strip(),)).fetchone()
                if row:
                    return Policyholder.from_dict(dict(row))
        except Exception as e:
            print(f"Error finding SQLite policyholder by name: {e}")
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
    Save or insert a policyholder record into database.
    """
    payload = {
        "full_name": holder.full_name,
        "gender": holder.gender,
        "date_of_birth": holder.date_of_birth.isoformat() if hasattr(holder.date_of_birth, "isoformat") else holder.date_of_birth,
        "city": holder.city,
        "state": holder.state
    }
    
    if os.getenv("DB_PROVIDER") == "sqlite":
        try:
            with get_sqlite_conn() as conn:
                cursor = conn.cursor()
                if holder.policyholder_id:
                    cursor.execute(
                        """UPDATE policyholders SET full_name = ?, gender = ?, date_of_birth = ?, city = ?, state = ? 
                           WHERE policyholder_id = ?""",
                        (payload["full_name"], payload["gender"], payload["date_of_birth"], 
                         payload["city"], payload["state"], holder.policyholder_id)
                    )
                else:
                    cursor.execute(
                        """INSERT INTO policyholders (full_name, gender, date_of_birth, city, state) 
                           VALUES (?, ?, ?, ?, ?)""",
                        (payload["full_name"], payload["gender"], payload["date_of_birth"], 
                         payload["city"], payload["state"])
                    )
                    holder.policyholder_id = cursor.lastrowid
                conn.commit()
                row = conn.execute("SELECT * FROM policyholders WHERE policyholder_id = ?", (holder.policyholder_id,)).fetchone()
                if row:
                    return Policyholder.from_dict(dict(row))
        except Exception as e:
            print(f"Error saving SQLite policyholder: {e}")
        return holder

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
