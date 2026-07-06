from models import AuditLog
from database import db
from utils.logger import logger

def log_event(action: str, user_id: int = None, claim_id: int = None, details: str = None) -> AuditLog:
    """
    Log an event to the database audit log.
    Safely logs and commits, capturing system failures if logging fails.
    """
    try:
        log = AuditLog(
            user_id=user_id,
            claim_id=claim_id,
            action=action.upper(),
            details=details
        )
        db.session.add(log)
        db.session.commit()
        
        # Log to application log file as well
        logger.info(
            f"AUDIT LOG: Action='{action.upper()}', UserID={user_id}, "
            f"ClaimID={claim_id}, Details='{details or ''}'"
        )
        return log
    except Exception as e:
        # Fallback logging if database write fails to prevent server crash
        db.session.rollback()
        logger.error(
            f"CRITICAL: Failed to write database audit log: {e}. "
            f"Payload: Action='{action}', UserID={user_id}, ClaimID={claim_id}, Details='{details}'"
        )
        return None
