import os
from typing import List, Dict, Any, Tuple, Optional
from utils.supabase_client import supabase
from utils.sqlite_client import get_sqlite_conn
from utils.logger import logger

def create_audit_log(user_id: Optional[int], claim_id: Optional[int], action: str, details: Optional[str]) -> Optional[Dict[str, Any]]:
    """
    Insert a new audit log record into database.
    """
    if os.getenv("DB_PROVIDER") == "sqlite":
        try:
            with get_sqlite_conn() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO audit_logs (user_id, claim_id, action, details) VALUES (?, ?, ?, ?)",
                    (user_id, claim_id, action.upper(), details)
                )
                log_id = cursor.lastrowid
                conn.commit()
                row = conn.execute("SELECT * FROM audit_logs WHERE log_id = ?", (log_id,)).fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error creating SQLite audit log: {e}")
            return None

    payload = {
        "user_id": user_id,
        "claim_id": claim_id,
        "action": action.upper(),
        "details": details
    }
    try:
        res = supabase.table("audit_logs").insert(payload).execute()
        return res.data[0] if res.data else None
    except Exception as e:
        logger.error(f"Error creating audit log: {e}")
        raise

def get_paginated_audit_logs(page: int = 1, per_page: int = 20) -> Tuple[List[Dict[str, Any]], int]:
    """
    Fetch paginated audit log entries from database.
    """
    if os.getenv("DB_PROVIDER") == "sqlite":
        try:
            with get_sqlite_conn() as conn:
                count_row = conn.execute("SELECT COUNT(*) as count FROM audit_logs").fetchone()
                total = count_row["count"] if count_row else 0
                
                start = (page - 1) * per_page
                rows = conn.execute(
                    "SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT ? OFFSET ?",
                    (per_page, start)
                ).fetchall()
                
                return [dict(r) for r in rows], total
        except Exception as e:
            logger.error(f"Error querying SQLite paginated audit logs: {e}")
            return [], 0

    try:
        start = (page - 1) * per_page
        end = start + per_page - 1
        
        res = supabase.table("audit_logs").select("*", count="exact").order("timestamp", desc=True).range(start, end).execute()
        
        logs_list = res.data if res.data else []
        total = res.count if res.count is not None else len(logs_list)
        
        return logs_list, total
    except Exception as e:
        logger.error(f"Error querying paginated audit logs (page={page}, per_page={per_page}): {e}")
        raise
    return [], 0
