"""
===========================================================
Healthcare Fraud Detection System
Notifications Routes (Controller)
===========================================================
"""

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.notification_service import get_user_notifications, mark_notification_as_read
from utils.api_response import success_response, error_response

notifications_bp = Blueprint("notifications", __name__)

@notifications_bp.route("", methods=["GET"])
@jwt_required()
def get_notifications():
    """
    GET /api/notifications
    Retrieves unread notifications for the active authenticated user.
    """
    try:
        user_id = int(get_jwt_identity())
        notifications = get_user_notifications(user_id)
        return success_response(
            data=notifications,
            message="Notifications retrieved successfully"
        )
    except Exception as e:
        return error_response(
            message=f"Failed to fetch notifications: {str(e)}",
            status_code=500
        )

@notifications_bp.route("/<int:notification_id>/read", methods=["PATCH"])
@jwt_required()
def mark_read(notification_id: int):
    """
    PATCH /api/notifications/{id}/read
    Marks the specified notification as read.
    """
    try:
        success = mark_notification_as_read(notification_id)
        if not success:
            return error_response(
                message="Notification not found or update failed",
                status_code=404
            )
        return success_response(
            message="Notification marked as read successfully"
        )
    except Exception as e:
        return error_response(
            message=f"Failed to update notification: {str(e)}",
            status_code=500
        )
