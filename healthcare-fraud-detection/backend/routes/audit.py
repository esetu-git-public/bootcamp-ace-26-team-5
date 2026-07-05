from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from models import AuditLog
from middleware.role_auth import role_required
from utils.response import success_response, error_response

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
        pagination = AuditLog.query.order_by(AuditLog.timestamp.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        logs_list = [log.to_dict() for log in pagination.items]
        
        data = {
            "logs": logs_list,
            "total_items": pagination.total,
            "total_pages": pagination.pages,
            "current_page": pagination.page,
            "per_page": pagination.per_page
        }
        
        return success_response(data=data, message="Audit logs retrieved successfully")
        
    except Exception as e:
        return error_response(
            message=f"Failed to query audit logs: {str(e)}",
            status_code=500
        )
