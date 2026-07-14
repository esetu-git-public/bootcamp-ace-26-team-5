from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

from services.dashboard_service import get_dashboard
from middleware.role_auth import role_required
from utils.response import success_response, error_response

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("", methods=["GET"])
@jwt_required()
@role_required("admin")
def get_dashboard_root():
    """
    GET /api/dashboard
    Restricted to Admins. Required for compliance with integration tests.
    """
    try:
        user_id = int(get_jwt_identity())
        data = get_dashboard("admin", user_id)
        return success_response(data=data, message="Dashboard analytics retrieved successfully")
    except Exception as e:
        return error_response(message=f"Failed to generate dashboard statistics: {str(e)}", status_code=500)


@dashboard_bp.route("/admin", methods=["GET"])
@jwt_required()
@role_required("admin")
def get_dashboard_admin():
    """
    GET /api/dashboard/admin
    Restricted to Admins.
    """
    try:
        user_id = int(get_jwt_identity())
        data = get_dashboard("admin", user_id)
        return success_response(data=data, message="Admin dashboard statistics retrieved")
    except Exception as e:
        return error_response(message=f"Failed to query admin stats: {str(e)}", status_code=500)


@dashboard_bp.route("/officer", methods=["GET"])
@jwt_required()
@role_required("admin", "employee")
def get_dashboard_officer():
    """
    GET /api/dashboard/officer
    Restricted to Claims Officers.
    """
    try:
        user_id = int(get_jwt_identity())
        data = get_dashboard("employee", user_id)
        return success_response(data=data, message="Officer dashboard statistics retrieved")
    except Exception as e:
        return error_response(message=f"Failed to query officer stats: {str(e)}", status_code=500)


@dashboard_bp.route("/customer", methods=["GET"])
@jwt_required()
@role_required("customer")
def get_dashboard_customer():
    """
    GET /api/dashboard/customer
    Restricted to Policyholders.
    """
    try:
        user_id = int(get_jwt_identity())
        data = get_dashboard("customer", user_id)
        return success_response(data=data, message="Customer dashboard statistics retrieved")
    except Exception as e:
        return error_response(message=f"Failed to query customer stats: {str(e)}", status_code=500)
