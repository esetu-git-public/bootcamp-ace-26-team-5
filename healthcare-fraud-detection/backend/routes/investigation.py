from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from models import InsuranceClaim, FraudPrediction
from middleware.role_auth import role_required
from utils.response import success_response, error_response

investigation_bp = Blueprint("investigation", __name__)

@investigation_bp.route("", methods=["GET"])
@jwt_required()
@role_required("admin", "investigator", "supervisor")
def get_investigation_queue():
    """
    GET /api/investigation
    Retrieves the queue of claims flagged as high-risk that require manual review.
    """
    try:
        # Join claims with predictions where risk_level is High and status is under_review or submitted
        high_risk_claims = InsuranceClaim.query.join(
            FraudPrediction, InsuranceClaim.claim_id == FraudPrediction.claim_id
        ).filter(
            FraudPrediction.risk_level == "High",
            InsuranceClaim.claim_status.in_(["submitted", "under_review"])
        ).order_by(InsuranceClaim.created_at.desc()).all()
        
        claims_list = []
        for claim in high_risk_claims:
            claim_dict = claim.to_dict()
            claim_dict["prediction"] = claim.prediction.to_dict()
            claims_list.append(claim_dict)
            
        return success_response(
            data=claims_list,
            message="Investigation queue retrieved successfully"
        )
    except Exception as e:
        return error_response(
            message=f"Failed to fetch investigation queue: {str(e)}",
            status_code=500
        )
