from models import AuditLog
from utils.supabase_client import supabase
from utils.logger import logger

def log_event(action: str, user_id: int = None, claim_id: int = None, details: str = None) -> AuditLog:
    """
    Log an event to the database audit log.
    Safely logs and commits, capturing system failures if logging fails.
    """
    payload = {
        "user_id": user_id,
        "claim_id": claim_id,
        "action": action.upper(),
        "details": details
    }
    try:
        res = supabase.table("audit_logs").insert(payload).execute()
        
        # Log to application log file as well
        logger.info(
            f"AUDIT LOG: Action='{action.upper()}', UserID={user_id}, "
            f"ClaimID={claim_id}, Details='{details or ''}'"
        )
        if res.data:
            return AuditLog.from_dict(res.data[0])
        return None
    except Exception as e:
        # Fallback logging if database write fails to prevent server crash
        logger.error(
            f"CRITICAL: Failed to write database audit log: {e}. "
            f"Payload: Action='{action}', UserID={user_id}, ClaimID={claim_id}, Details='{details}'"
        )
        return None
