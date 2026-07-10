from models import User
from utils.supabase_client import supabase

def find_user_by_id(user_id: int) -> User:
    """
    Retrieve a user by their unique primary key ID.
    """
    try:
        res = supabase.table("users").select("*").eq("user_id", user_id).execute()
        if res.data:
            return User.from_dict(res.data[0])
    except Exception as e:
        print(f"Error finding user by ID: {e}")
    return None


def find_user_by_email(email: str) -> User:
    """
    Retrieve a user by their email address.
    """
    if not email:
        return None
    try:
        res = supabase.table("users").select("*").eq("email", email.strip().lower()).execute()
        if res.data:
            return User.from_dict(res.data[0])
    except Exception as e:
        print(f"Error finding user by email: {e}")
    return None


def create_user(full_name: str, email: str, password_hash: str, role: str = "employee") -> User:
    """
    Insert a new user record into the database.
    """
    payload = {
        "full_name": full_name.strip(),
        "email": email.strip().lower(),
        "password_hash": password_hash,
        "role": role.strip().lower()
    }
    try:
        res = supabase.table("users").insert(payload).execute()
        if res.data:
            return User.from_dict(res.data[0])
    except Exception as e:
        print(f"Error creating user: {e}")
    return None
