import os
from models import User
from utils.supabase_client import supabase
from utils.sqlite_client import get_sqlite_conn

def find_user_by_id(user_id: int) -> User:
    """
    Retrieve a user by their unique primary key ID.
    """
    if os.getenv("DB_PROVIDER") == "sqlite":
        try:
            with get_sqlite_conn() as conn:
                row = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
                if row:
                    return User.from_dict(dict(row))
        except Exception as e:
            print(f"Error finding SQLite user by ID: {e}")
        return None

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
    if os.getenv("DB_PROVIDER") == "sqlite":
        try:
            with get_sqlite_conn() as conn:
                row = conn.execute("SELECT * FROM users WHERE LOWER(email) = ?", (email.strip().lower(),)).fetchone()
                if row:
                    return User.from_dict(dict(row))
        except Exception as e:
            print(f"Error finding SQLite user by email: {e}")
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
    if os.getenv("DB_PROVIDER") == "sqlite":
        try:
            with get_sqlite_conn() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (full_name, email, password_hash, role) VALUES (?, ?, ?, ?)",
                    (full_name.strip(), email.strip().lower(), password_hash, role.strip().lower())
                )
                user_id = cursor.lastrowid
                conn.commit()
                row = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
                if row:
                    return User.from_dict(dict(row))
        except Exception as e:
            print(f"Error creating SQLite user: {e}")
        return None

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


def find_users_by_role(role: str) -> list[User]:
    """
    Retrieve all users with a specific role.
    """
    if os.getenv("DB_PROVIDER") == "sqlite":
        try:
            with get_sqlite_conn() as conn:
                rows = conn.execute("SELECT * FROM users WHERE LOWER(role) = ?", (role.strip().lower(),)).fetchall()
                return [User.from_dict(dict(r)) for r in rows]
        except Exception as e:
            print(f"Error finding SQLite users by role: {e}")
        return []

    try:
        res = supabase.table("users").select("*").eq("role", role.strip().lower()).execute()
        if res.data:
            return [User.from_dict(d) for d in res.data]
    except Exception as e:
        print(f"Error finding users by role: {e}")
    return []
