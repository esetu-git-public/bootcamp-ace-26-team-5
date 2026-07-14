from models import AuditLog
from repositories.audit_repository import create_audit_log
from utils.logger import logger

def log_event(action: str, user_id: int = None, claim_id: int = None, details: str = None) -> AuditLog:
    """
    Log an event to the database audit log.
    Safely logs and commits, capturing system failures if logging fails.
    """
    try:
        # Log to database using repository helper
        log_data = create_audit_log(user_id, claim_id, action, details)
        
        # Log to application log file as well
        logger.info(
            f"AUDIT LOG: Action='{action.upper()}', UserID={user_id}, "
            f"ClaimID={claim_id}, Details='{details or ''}'"
        )
        if log_data:
            return AuditLog.from_dict(log_data)
        return None
    except Exception as e:
        logger.error(
            f"CRITICAL: Failed to write database audit log: {e}. "
            f"Payload: Action='{action}', UserID={user_id}, ClaimID={claim_id}, Details='{details}'"
        )
        return None
