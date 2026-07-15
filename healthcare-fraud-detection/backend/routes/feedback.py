from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from middleware.role_auth import role_required
from utils.response import success_response, error_response
from repositories.feedback_repository import (
    create_feedback,
    get_feedback_by_claim_id,
    get_all_feedback,
    get_feedback_stats
)

feedback_bp = Blueprint("feedback", __name__)

@feedback_bp.route("", methods=["POST"])
@jwt_required()
@role_required("admin", "employee")
def submit_claim_feedback():
    """
    POST /api/feedback
    Submit user feedback on a model's prediction.
    """
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json() or {}

        claim_id = data.get("claim_id")
        if not claim_id:
            return error_response(message="claim_id is required", status_code=400)

        # Check if feedback already exists for this claim
        existing = get_feedback_by_claim_id(claim_id)
        if existing:
            return error_response(message="Feedback has already been submitted for this claim.", status_code=400)

        is_incorrect = bool(data.get("is_incorrect", False))
        actual_label = data.get("actual_label", "Not Fraud")
        feedback_text = data.get("feedback_text", "")
        model_version = data.get("model_version", "v1.0")

        fb = create_feedback(
            claim_id=claim_id,
            user_id=user_id,
            is_incorrect=is_incorrect,
            actual_label=actual_label,
            feedback_text=feedback_text,
            model_version=model_version
        )

        if not fb:
            return error_response(message="Failed to save model feedback.", status_code=500)

        return success_response(
            data=fb.to_dict(),
            message="Model feedback submitted successfully",
            status_code=201
        )
    except Exception as e:
        return error_response(message=f"Error submitting feedback: {str(e)}", status_code=500)


@feedback_bp.route("/claim/<int:claim_id>", methods=["GET"])
@jwt_required()
def get_claim_feedback(claim_id):
    """
    GET /api/feedback/claim/<claim_id>
    Retrieve feedback details for a specific claim.
    """
    try:
        fb = get_feedback_by_claim_id(claim_id)
        if not fb:
            return success_response(data=None, message="No feedback found for this claim")
        return success_response(data=fb.to_dict(), message="Model feedback retrieved successfully")
    except Exception as e:
        return error_response(message=f"Error retrieving feedback: {str(e)}", status_code=500)


@feedback_bp.route("/stats", methods=["GET"])
@jwt_required()
@role_required("admin", "employee")
def get_metrics_stats():
    """
    GET /api/feedback/stats
    Retrieve aggregated model performance and disagreement metrics.
    """
    try:
        stats = get_feedback_stats()
        return success_response(data=stats, message="Model failure statistics retrieved successfully")
    except Exception as e:
        return error_response(message=f"Error generating feedback stats: {str(e)}", status_code=500)


@feedback_bp.route("", methods=["GET"])
@jwt_required()
@role_required("admin", "employee")
def list_feedback():
    """
    GET /api/feedback
    List all model feedback submissions.
    """
    try:
        feedback_list = get_all_feedback()
        return success_response(data=feedback_list, message="All model feedback entries retrieved successfully")
    except Exception as e:
        return error_response(message=f"Error listing feedback: {str(e)}", status_code=500)
