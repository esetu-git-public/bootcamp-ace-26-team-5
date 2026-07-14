import os
from typing import List, Dict, Any
from utils.supabase_client import supabase
from utils.sqlite_client import get_sqlite_conn
from utils.logger import logger

def create_notification(recipient_id: int, message: str, severity: str = "info") -> bool:
    """
    Insert a new notification into database.
    """
    if os.getenv("DB_PROVIDER") == "sqlite":
        try:
            with get_sqlite_conn() as conn:
                conn.execute(
                    "INSERT INTO notifications (recipient_id, message, severity, is_read) VALUES (?, ?, ?, ?)",
                    (recipient_id, message, severity, 0)
                )
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error creating SQLite notification: {e}")
            return False

    try:
        payload = {
            "recipient_id": recipient_id,
            "message": message,
            "severity": severity,
            "is_read": False
        }
        res = supabase.table("notifications").insert(payload).execute()
        return bool(res.data)
    except Exception as e:
        logger.error(f"Error creating notification for user {recipient_id}: {e}")
        raise

def find_unread_notifications_by_recipient(user_id: int) -> List[Dict[str, Any]]:
    """
    Query unread notifications for a user, ordered by creation date descending.
    """
    if os.getenv("DB_PROVIDER") == "sqlite":
        try:
            with get_sqlite_conn() as conn:
                rows = conn.execute(
                    "SELECT * FROM notifications WHERE recipient_id = ? AND is_read = 0 ORDER BY created_at DESC",
                    (user_id,)
                ).fetchall()
                res = []
                for r in rows:
                    d = dict(r)
                    d["is_read"] = bool(d["is_read"])
                    res.append(d)
                return res
        except Exception as e:
            logger.error(f"Error finding SQLite unread notifications: {e}")
            return []

    try:
        res = supabase.table("notifications").select("*").eq("recipient_id", user_id).eq("is_read", False).order("created_at", desc=True).execute()
        return res.data if res.data else []
    except Exception as e:
        logger.error(f"Error finding unread notifications for user {user_id}: {e}")
        raise

def mark_notification_as_read(notification_id: int) -> bool:
    """
    Mark a specific notification as read in database.
    """
    if os.getenv("DB_PROVIDER") == "sqlite":
        try:
            with get_sqlite_conn() as conn:
                conn.execute(
                    "UPDATE notifications SET is_read = 1 WHERE notification_id = ?",
                    (notification_id,)
                )
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error marking SQLite notification as read: {e}")
            return False

    try:
        res = supabase.table("notifications").update({"is_read": True}).eq("notification_id", notification_id).execute()
        return bool(res.data)
    except Exception as e:
        logger.error(f"Error marking notification {notification_id} as read: {e}")
        raise
