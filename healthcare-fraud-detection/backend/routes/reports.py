from flask import Blueprint
from flask_jwt_extended import jwt_required

from middleware.role_auth import role_required
from utils.response import success_response, error_response
from utils.supabase_client import supabase

reports_bp = Blueprint("reports", __name__)

@reports_bp.route("", methods=["GET"])
@jwt_required()
@role_required("admin")
def generate_reports():
    """
    GET /api/reports
    Compiles detailed analytical reports for export (claims breakdown, fraud rates, and investigation queues).
    Restricted to Admins.
    """
    try:
        # 1. Claims Report Data
        res_claims = supabase.table("insurance_claims").select("claim_status, claim_amount").execute()
        claims_by_status = {}
        if res_claims.data:
            for row in res_claims.data:
                status = row.get("claim_status", "submitted")
                amount = float(row.get("claim_amount", 0.0))
                if status not in claims_by_status:
                    claims_by_status[status] = {"count": 0, "total_amount": 0.0}
                claims_by_status[status]["count"] += 1
                claims_by_status[status]["total_amount"] += amount
                
        claims_report = [
            {
                "status": status,
                "count": info["count"],
                "total_amount": round(info["total_amount"], 2)
            }
            for status, info in claims_by_status.items()
        ]

        # 2. Fraud Flagged Report Data
        res_preds = supabase.table("fraud_predictions").select("*, claim:insurance_claims(*)").eq("predicted_label", "Fraud").order("fraud_probability", desc=True).execute()
        fraud_report = []
        if res_preds.data:
            for row in res_preds.data:
                claim_data = row.get("claim")
                if claim_data:
                    if isinstance(claim_data, list) and len(claim_data) > 0:
                        claim_data = claim_data[0]
                    
                    if isinstance(claim_data, dict):
                        fraud_report.append({
                            "claim_number": claim_data.get("claim_number"),
                            "claim_amount": claim_data.get("claim_amount"),
                            "claim_status": claim_data.get("claim_status"),
                            "fraud_probability": row.get("fraud_probability"),
                            "risk_level": row.get("risk_level"),
                            "reasons": row.get("remarks")
                        })

        # 3. Investigation Queue Report Data
        res_review = supabase.table("insurance_claims").select("*, prediction:fraud_predictions(*)").eq("claim_status", "under_review").execute()
        investigation_report = []
        if res_review.data:
            for row in res_review.data:
                predictions = row.get("prediction") or row.get("fraud_predictions")
                risk_level = "Low"
                if predictions:
                    if isinstance(predictions, list) and len(predictions) > 0:
                        risk_level = predictions[0].get("risk_level", "Low")
                    elif isinstance(predictions, dict):
                        risk_level = predictions.get("risk_level", "Low")
                        
                investigation_report.append({
                    "claim_number": row.get("claim_number"),
                    "claim_amount": row.get("claim_amount"),
                    "claim_type": row.get("claim_type"),
                    "risk_level": risk_level,
                    "submitted_at": row.get("created_at")
                })

        data = {
            "claims_report": claims_report,
            "fraud_report": fraud_report,
            "investigation_report": investigation_report
        }
        
        return success_response(data=data, message="Export-ready reports generated successfully")
        
    except Exception as e:
        return error_response(
            message=f"Failed to generate export reports: {str(e)}",
            status_code=500
        )
