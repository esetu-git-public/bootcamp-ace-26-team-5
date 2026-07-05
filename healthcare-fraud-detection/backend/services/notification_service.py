from utils.logger import logger
from datetime import datetime

# In-memory store for simulated in-app notifications
_in_app_notifications = []

def send_notification(recipient_id: int, message: str, channel: str = "in_app", severity: str = "info") -> bool:
    """
    Send a notification to a user.
    Initially supports 'in_app' and 'backend_event'.
    Designed to easily plug in Email, SMS, and WhatsApp adapters.
    """
    try:
        # 1. Log backend event
        logger.info(
            f"NOTIFICATION EVENT: Channel='{channel}', RecipientID={recipient_id}, "
            f"Severity='{severity.upper()}', Message='{message}'"
        )

        # 2. Process based on channel selection
        if channel == "in_app":
            _in_app_notifications.append({
                "recipient_id": recipient_id,
                "message": message,
                "severity": severity,
                "read": False,
                "timestamp": datetime.utcnow().isoformat() if "datetime" in globals() else "2026-07-05T22:00:00"
            })
            return True
            
        elif channel == "email":
            # Future integration hook: e.g., send_smtp_email(recipient_id, message)
            logger.info("Email adapter stub executed.")
            return True
            
        elif channel == "sms":
            # Future integration hook: e.g., send_twilio_sms(recipient_id, message)
            logger.info("SMS adapter stub executed.")
            return True
            
        elif channel == "whatsapp":
            # Future integration hook: e.g., send_whatsapp_message(recipient_id, message)
            logger.info("WhatsApp adapter stub executed.")
            return True
            
        return False
        
    except Exception as e:
        logger.error(f"Failed to dispatch notification: {e}")
        return False


def get_user_notifications(user_id: int) -> list[dict]:
    """
    Retrieve unread simulated in-app notifications for a user.
    """
    return [n for n in _in_app_notifications if n["recipient_id"] == user_id]
