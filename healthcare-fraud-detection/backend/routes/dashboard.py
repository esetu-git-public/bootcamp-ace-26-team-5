from flask import Blueprint
from flask_jwt_extended import jwt_required

from services.dashboard_service import get_dashboard_summary
from utils.response import success_response, error_response

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("", methods=["GET"])
@jwt_required()
def get_dashboard():
    """
    GET /api/dashboard
    Returns summary KPIs, monthly claims counts, risk distribution, and common fraud indicators.
    """
    try:
        data = get_dashboard_summary()
        return success_response(data=data, message="Dashboard analytics retrieved successfully")
    except Exception as e:
        return error_response(message=f"Failed to generate dashboard statistics: {str(e)}", status_code=500)
