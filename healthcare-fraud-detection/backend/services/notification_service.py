import os
from utils.logger import logger
from utils.supabase_client import supabase
from repositories.notification_repository import create_notification
from utils.sqlite_client import get_sqlite_conn

def send_notification(recipient_id: int, message: str, channel: str = "in_app", severity: str = "info") -> bool:
    """
    Send a notification to a user.
    Saves to the notifications table in database.
    """
    try:
        # 1. Log notification event
        logger.info(
            f"NOTIFICATION EVENT: Channel='{channel}', RecipientID={recipient_id}, "
            f"Severity='{severity.upper()}', Message='{message}'"
        )

        # 2. Process based on channel selection
        if channel == "in_app":
            return create_notification(recipient_id=recipient_id, message=message, severity=severity)
            
        elif channel == "email":
            logger.info("Email adapter stub executed.")
            return True
            
        elif channel == "sms":
            logger.info("SMS adapter stub executed.")
            return True
            
        elif channel == "whatsapp":
            logger.info("WhatsApp adapter stub executed.")
            return True
            
        return False
        
    except Exception as e:
        logger.error(f"Failed to dispatch notification: {e}")
        return False


def get_user_notifications(user_id: int) -> list[dict]:
    """
    Retrieve notifications for a user, degrading gracefully if missing.
    """
    if os.getenv("DB_PROVIDER") == "sqlite":
        try:
            with get_sqlite_conn() as conn:
                rows = conn.execute(
                    "SELECT * FROM notifications WHERE recipient_id = ? ORDER BY created_at DESC",
                    (user_id,)
                ).fetchall()
                res = []
                for r in rows:
                    d = dict(r)
                    d["is_read"] = bool(d["is_read"])
                    res.append(d)
                return res
        except Exception as e:
            logger.error(f"Error fetching SQLite user notifications: {e}")
            return []

    try:
        res = supabase.table("notifications").select("*").eq("recipient_id", user_id).execute()
        return res.data if res.data else []
    except Exception as db_err:
        logger.warning(f"Graceful degradation: notifications table missing or DB read failed: {db_err}")
        return []
