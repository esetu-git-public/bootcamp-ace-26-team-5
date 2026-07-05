from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from repositories.claim_repository import (
    find_claim_by_id,
    get_paginated_claims,
    delete_claim as db_delete_claim
)
from validators.claim_validator import validate_claim_payload
from services.claim_service import (
    create_claim_from_payload,
    update_claim_status_service
)
from middleware.role_auth import role_required
from utils.response import success_response, error_response
from services.audit_service import log_event
from models import FraudPrediction

claim_bp = Blueprint("claims", __name__)

@claim_bp.route("", methods=["POST"])
@jwt_required()
def create_claim():
    """
    POST /api/claims
    Creates a new insurance claim and returns the scored ML prediction.
    """
    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True)

    # Validate input
    is_valid, err_msg = validate_claim_payload(data)
    if not is_valid:
        return error_response(message=err_msg, status_code=400)

    try:
        # Create claim (runs ML model internally & sets initial routed status)
        claim = create_claim_from_payload(data, user_id=user_id)
        
        # Build response with prediction details
        claim_dict = claim.to_dict()
        if claim.prediction:
            claim_dict["prediction"] = claim.prediction.to_dict()
            
        return success_response(
            data=claim_dict,
            message="Claim created and analyzed successfully",
            status_code=201
        )
    except Exception as e:
        return error_response(message=f"Failed to create claim: {str(e)}", status_code=500)


@claim_bp.route("", methods=["GET"])
@jwt_required()
def get_claims():
    """
    GET /api/claims
    Queries all claims. Supports pagination, sorting, status filtering, and query searching.
    """
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    sort_by = request.args.get("sort_by", "created_at", type=str)
    order = request.args.get("order", "desc", type=str)
    
    status = request.args.get("status", None, type=str)
    claim_type = request.args.get("claim_type", None, type=str)
    search_query = request.args.get("q", None, type=str)

    filters = {
        "claim_status": status,
        "claim_type": claim_type,
        "search_query": search_query
    }

    try:
        pagination = get_paginated_claims(
            filters=filters,
            sort_by=sort_by,
            order=order,
            page=page,
            per_page=per_page
        )
        
        claims_list = []
        for claim in pagination.items:
            claim_dict = claim.to_dict()
            if claim.prediction:
                claim_dict["prediction"] = claim.prediction.to_dict()
            claims_list.append(claim_dict)

        data = {
            "claims": claims_list,
            "total_items": pagination.total,
            "total_pages": pagination.pages,
            "current_page": pagination.page,
            "per_page": pagination.per_page,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev
        }
        
        return success_response(data=data, message="Claims retrieved successfully")
    except Exception as e:
        return error_response(message=f"Failed to retrieve claims: {str(e)}", status_code=500)


@claim_bp.route("/<int:claim_id>", methods=["GET"])
@jwt_required()
def get_claim_details(claim_id):
    """
    GET /api/claims/{id}
    Retrieves detailed info of a single claim along with its prediction.
    """
    claim = find_claim_by_id(claim_id)
    if not claim:
        return error_response(message="Claim not found", status_code=404)

    claim_dict = claim.to_dict()
    if claim.prediction:
        claim_dict["prediction"] = claim.prediction.to_dict()
        
    return success_response(data=claim_dict, message="Claim details retrieved successfully")


@claim_bp.route("/<int:claim_id>/status", methods=["PATCH"])
@jwt_required()
@role_required("admin", "employee", "investigator", "supervisor")
def update_claim_status(claim_id):
    """
    PATCH /api/claims/{id}/status
    Updates the status of a claim (approved, rejected, under_review, submitted).
    Restricted to authorized roles.
    """
    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True)
    if not data or "status" not in data:
        return error_response("Status field is required", 400)

    new_status = data.get("status").strip().lower()
    
    success, message = update_claim_status_service(claim_id, new_status, user_id)
    if not success:
        return error_response(message=message, status_code=400 if "Invalid" in message else 404)

    return success_response(message=message)


@claim_bp.route("/<int:claim_id>", methods=["DELETE"])
@jwt_required()
@role_required("admin")
def delete_claim(claim_id):
    """
    DELETE /api/claims/{id}
    Deletes a claim record from the database. Restricted to administrators.
    """
    user_id = int(get_jwt_identity())
    
    # Check claim existence for logging details
    claim = find_claim_by_id(claim_id)
    if not claim:
        return error_response("Claim not found", 404)
        
    claim_num = claim.claim_number
    success = db_delete_claim(claim_id)
    if not success:
        return error_response("Failed to delete claim", 500)

    # Log audit event
    log_event(
        action="CLAIM_DELETION",
        user_id=user_id,
        details=f"Admin deleted claim ID {claim_id} (Claim number: {claim_num})."
    )

    return success_response(message=f"Claim {claim_num} deleted successfully")
