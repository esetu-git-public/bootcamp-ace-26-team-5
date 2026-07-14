from utils.logger import logger
from utils.supabase_client import supabase
from datetime import datetime

def send_notification(recipient_id: int, message: str, channel: str = "in_app", severity: str = "info") -> bool:
    """
    Send a notification to a user.
    Saves to the notifications table in Supabase, degrading gracefully if the table is missing.
    """
    try:
        # 1. Log notification event
        logger.info(
            f"NOTIFICATION EVENT: Channel='{channel}', RecipientID={recipient_id}, "
            f"Severity='{severity.upper()}', Message='{message}'"
        )

        # 2. Process based on channel selection
        if channel == "in_app":
            payload = {
                "recipient_id": recipient_id,
                "message": message,
                "severity": severity,
                "is_read": False
            }
            try:
                res = supabase.table("notifications").insert(payload).execute()
                return bool(res.data)
            except Exception as db_err:
                logger.warning(f"Graceful degradation: notifications table missing or DB write failed: {db_err}")
                return False
            
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
    Retrieve notifications for a user from Supabase, degrading gracefully if missing.
    """
    try:
        res = supabase.table("notifications").select("*").eq("recipient_id", user_id).execute()
        return res.data if res.data else []
    except Exception as db_err:
        logger.warning(f"Graceful degradation: notifications table missing or DB read failed: {db_err}")
        return []
