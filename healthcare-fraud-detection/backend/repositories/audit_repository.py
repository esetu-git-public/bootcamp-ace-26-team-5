"""
===========================================================
Healthcare Fraud Detection System
Audit Repository
===========================================================

This module manages database interactions for audit logs.
"""

from typing import List, Dict, Any, Tuple, Optional
from utils.supabase_client import supabase
from utils.logger import logger

def create_audit_log(user_id: Optional[int], claim_id: Optional[int], action: str, details: Optional[str]) -> Optional[Dict[str, Any]]:
    """
    Insert a new audit log record into Supabase.
    """
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
    Fetch paginated audit log entries from Supabase.
    
    Args:
        page (int): Page number (1-indexed). Defaults to 1.
        per_page (int): Items per page. Defaults to 20.
        
    Returns:
        tuple: (list of audit logs, total count of logs)
    """
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

