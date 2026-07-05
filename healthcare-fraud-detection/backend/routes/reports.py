from flask import Blueprint
from flask_jwt_extended import jwt_required

from models import InsuranceClaim, FraudPrediction
from middleware.role_auth import role_required
from utils.response import success_response, error_response
from database import db

reports_bp = Blueprint("reports", __name__)

@reports_bp.route("", methods=["GET"])
@jwt_required()
@role_required("admin", "supervisor")
def generate_reports():
    """
    GET /api/reports
    Compiles detailed analytical reports for export (claims breakdown, fraud rates, and investigation queues).
    """
    try:
        # 1. Claims Report Data
        claims_by_status = db.session.query(
            InsuranceClaim.claim_status,
            db.func.count(InsuranceClaim.claim_id),
            db.func.sum(InsuranceClaim.claim_amount)
        ).group_by(InsuranceClaim.claim_status).all()
        
        claims_report = [
            {
                "status": row[0],
                "count": row[1],
                "total_amount": round(row[2] or 0.0, 2)
            }
            for row in claims_by_status
        ]

        # 2. Fraud Flagged Report Data
        high_risk_flagged = InsuranceClaim.query.join(
            FraudPrediction, InsuranceClaim.claim_id == FraudPrediction.claim_id
        ).filter(
            FraudPrediction.predicted_label == "Fraud"
        ).order_by(FraudPrediction.fraud_probability.desc()).all()
        
        fraud_report = [
            {
                "claim_number": c.claim_number,
                "claim_amount": c.claim_amount,
                "claim_status": c.claim_status,
                "fraud_probability": c.prediction.fraud_probability,
                "risk_level": c.prediction.risk_level,
                "reasons": c.prediction.remarks
            }
            for c in high_risk_flagged
        ]

        # 3. Investigation Queue Report Data
        under_review_flagged = InsuranceClaim.query.filter_by(claim_status="under_review").all()
        investigation_report = [
            {
                "claim_number": c.claim_number,
                "claim_amount": c.claim_amount,
                "claim_type": c.claim_type,
                "risk_level": c.prediction.risk_level if c.prediction else "Low",
                "submitted_at": c.created_at.isoformat() if c.created_at else None
            }
            for c in under_review_flagged
        ]

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
