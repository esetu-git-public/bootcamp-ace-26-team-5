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
