import os
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
    """
    # 1. SQLite Fallback Provider
    if os.getenv("DB_PROVIDER") == "sqlite":
        from utils.sqlite_client import get_sqlite_conn
        try:
            with get_sqlite_conn() as conn:
                # Query claims with risk in High/Medium or under review
                rows = conn.execute("""
                    SELECT c.*, p.predicted_label, p.fraud_probability, p.risk_level, p.model_version, p.remarks
                    FROM insurance_claims c
                    JOIN fraud_predictions p ON c.claim_id = p.claim_id
                    WHERE p.risk_level IN ('High', 'Medium') AND c.claim_status IN ('submitted', 'under_review')
                    ORDER BY c.claim_date DESC
                """).fetchall()
                
                claims_list = []
                for row in rows:
                    claim_dict = dict(row)
                    
                    # Nest policy details manually
                    policy_id = claim_dict.get("policy_id")
                    policy_row = conn.execute("SELECT * FROM insurance_policies WHERE policy_id = ?", (policy_id,)).fetchone()
                    policy_dict = dict(policy_row) if policy_row else None
                    
                    if policy_dict:
                        holder_id = policy_dict.get("policyholder_id")
                        holder_row = conn.execute("SELECT * FROM policyholders WHERE policyholder_id = ?", (holder_id,)).fetchone()
                        policy_dict["policyholder"] = dict(holder_row) if holder_row else None
                        
                    claim_dict["policy"] = policy_dict
                    claim_dict["police_report_available"] = bool(claim_dict.get("police_report_available"))
                    
                    # Build prediction dict
                    pred_dict = {
                        "predicted_label": claim_dict.get("predicted_label"),
                        "fraud_probability": claim_dict.get("fraud_probability"),
                        "raw_probability": claim_dict.get("raw_probability"),
                        "business_rule_adjustment": claim_dict.get("business_rule_adjustment"),
                        "risk_level": claim_dict.get("risk_level"),
                        "model_version": claim_dict.get("model_version"),
                        "remarks": claim_dict.get("remarks")
                    }
                    claim_dict["prediction"] = pred_dict
                    claims_list.append(claim_dict)
                    
            return success_response(data=claims_list, message="Investigation queue retrieved successfully")
        except Exception as e:
            return error_response(message=f"Failed to fetch SQLite investigation queue: {str(e)}", status_code=500)

    # 2. Supabase Cloud Provider
    try:
        res = supabase.table("fraud_predictions").select(
            "*, claim:insurance_claims(*, policy:insurance_policies(*, policyholder:policyholders(*)))"
        ).in_("risk_level", ["High", "Medium"]).execute()
        
        claims_list = []
        if res.data:
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
                            "raw_probability": pred_data.get("raw_probability"),
                            "business_rule_adjustment": pred_data.get("business_rule_adjustment"),
                            "risk_level": pred_data.get("risk_level"),
                            "model_version": pred_data.get("model_version"),
                            "prediction_date": pred_data.get("prediction_date"),
                            "remarks": pred_data.get("remarks")
                        }
                        
                        claim_dict["police_report_available"] = bool(claim_dict.get("police_report_available"))
                        claim_dict["prediction"] = pred_dict
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
