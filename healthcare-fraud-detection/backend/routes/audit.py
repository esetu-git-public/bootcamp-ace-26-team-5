import os
from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from models import AuditLog
from middleware.role_auth import role_required
from utils.response import success_response, error_response
from utils.supabase_client import supabase

audit_bp = Blueprint("audit", __name__)

@audit_bp.route("", methods=["GET"])
@jwt_required()
@role_required("admin")
def get_audit_logs():
    """
    GET /api/audit
    Returns paginated system-wide audit logs. Restricted to admins.
    """
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    # 1. SQLite Fallback Provider
    if os.getenv("DB_PROVIDER") == "sqlite":
        from utils.sqlite_client import get_sqlite_conn
        try:
            with get_sqlite_conn() as conn:
                # Get total count
                total = conn.execute("SELECT COUNT(*) FROM audit_logs").fetchone()[0]
                
                # Fetch paginated logs joining with users
                log_rows = conn.execute("""
                    SELECT a.*, u.full_name as user_name
                    FROM audit_logs a
                    LEFT JOIN users u ON a.user_id = u.user_id
                    ORDER BY a.timestamp DESC
                    LIMIT ? OFFSET ?
                """, (per_page, (page - 1) * per_page)).fetchall()
                
                logs_list = []
                for row in log_rows:
                    log_dict = dict(row)
                    logs_list.append({
                        "log_id": log_dict.get("log_id"),
                        "action": log_dict.get("action"),
                        "details": log_dict.get("details"),
                        "timestamp": log_dict.get("timestamp"),
                        "user_id": log_dict.get("user_id"),
                        "claim_id": log_dict.get("claim_id"),
                        "user_name": log_dict.get("user_name") or "System"
                    })
                    
                total_pages = (total + per_page - 1) // per_page if per_page > 0 else 0
                data = {
                    "logs": logs_list,
                    "total_items": total,
                    "total_pages": total_pages,
                    "current_page": page,
                    "per_page": per_page
                }
                return success_response(data=data, message="Audit logs retrieved successfully")
        except Exception as e:
            return error_response(message=f"Database error: {e}", status_code=500)

    # 2. Supabase Cloud Provider
    try:
        start = (page - 1) * per_page
        end = start + per_page - 1
        
        res = supabase.table("audit_logs").select("*", count="exact").order("timestamp", desc=True).range(start, end).execute()
        
        logs_list = []
        if res.data:
            for log_data in res.data:
                logs_list.append(AuditLog.from_dict(log_data).to_dict())
                
        total = res.count if res.count is not None else len(logs_list)
        total_pages = (total + per_page - 1) // per_page if per_page > 0 else 0
        
        data = {
            "logs": logs_list,
            "total_items": total,
            "total_pages": total_pages,
            "current_page": page,
            "per_page": per_page
        }
        
        return success_response(data=data, message="Audit logs retrieved successfully")
        
    except Exception as e:
        return error_response(
            message=f"Failed to query audit logs: {str(e)}",
            status_code=500
        )
