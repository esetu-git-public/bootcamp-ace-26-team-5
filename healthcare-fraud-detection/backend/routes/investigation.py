from flask import Blueprint
from flask_jwt_extended import jwt_required

from middleware.role_auth import role_required
from utils.response import success_response, error_response
from utils.supabase_client import supabase

investigation_bp = Blueprint("investigation", __name__)

@investigation_bp.route("", methods=["GET"])
@jwt_required()
@role_required("admin", "employee")
def get_investigation_queue():
    """
    GET /api/investigation
    Retrieves the queue of claims flagged as high or medium risk that require manual review.
    Queries Supabase REST relation mappings.
    """
    try:
        # Fetch predictions with risk_level in High/Medium and nested claim data
        res = supabase.table("fraud_predictions").select(
            "*, claim:insurance_claims(*, policy:insurance_policies(*, policyholder:policyholders(*)))"
        ).in_("risk_level", ["High", "Medium"]).execute()
        
        claims_list = []
        if res.data:
            # Sort by prediction_date desc (as a proxy for claim creation date desc)
            sorted_preds = sorted(res.data, key=lambda x: x.get("prediction_date", ""), reverse=True)
            for pred_data in sorted_preds:
                claim_data = pred_data.get("claim")
                if claim_data:
                    if isinstance(claim_data, list) and len(claim_data) > 0:
                        claim_data = claim_data[0]
                        
                    if isinstance(claim_data, dict) and claim_data.get("claim_status") in ["submitted", "under_review"]:
                        claim_dict = claim_data.copy()
                        
                        pred_dict = {
                            "prediction_id": pred_data.get("prediction_id"),
                            "claim_id": pred_data.get("claim_id"),
                            "predicted_label": pred_data.get("predicted_label"),
                            "fraud_probability": pred_data.get("fraud_probability"),
                            "risk_level": pred_data.get("risk_level"),
                            "model_version": pred_data.get("model_version"),
                            "prediction_date": pred_data.get("prediction_date"),
                            "remarks": pred_data.get("remarks")
                        }
                        
                        claim_dict["police_report_available"] = bool(claim_dict.get("police_report_available"))
                        claim_dict["prediction"] = pred_dict
                        # Embed policy details if nested
                        claim_dict["policy_embedded"] = claim_data.get("policy")
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
