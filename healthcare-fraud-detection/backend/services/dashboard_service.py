from models import InsuranceClaim, FraudPrediction
from database import db
from collections import Counter
import re

def get_dashboard_summary() -> dict:
    """
    Compile all KPIs, risk distributions, averages, and trend aggregates
    required for the frontend dashboard and reports pages.
    """
    # 1. Core KPIs
    total_claims = InsuranceClaim.query.count()
    approved_claims = InsuranceClaim.query.filter_by(claim_status="approved").count()
    rejected_claims = InsuranceClaim.query.filter_by(claim_status="rejected").count()
    
    # ML Prediction-based KPIs
    fraud_detected = FraudPrediction.query.filter_by(predicted_label="Fraud").count()
    pending_review = InsuranceClaim.query.filter(
        InsuranceClaim.claim_status.in_(["submitted", "under_review"])
    ).count()

    # 2. Averages
    avg_claim = db.session.query(db.func.avg(InsuranceClaim.claim_amount)).scalar() or 0.0
    
    # 3. Risk Distribution
    risk_distribution = {
        "Low": FraudPrediction.query.filter_by(risk_level="Low").count(),
        "Medium": FraudPrediction.query.filter_by(risk_level="Medium").count(),
        "High": FraudPrediction.query.filter_by(risk_level="High").count(),
    }

    # 4. Monthly Time Series Trend (last 6 months)
    # Group claims count by YYYY-MM using sqlite strftime helper
    monthly_stats = db.session.query(
        db.func.strftime("%Y-%m", InsuranceClaim.claim_date),
        db.func.count(InsuranceClaim.claim_id)
    ).group_by(db.func.strftime("%Y-%m", InsuranceClaim.claim_date)).order_by(
        db.func.strftime("%Y-%m", InsuranceClaim.claim_date).asc()
    ).all()
    
    monthly_trend = [{"month": row[0], "claims": row[1]} for row in monthly_stats if row[0] is not None]

    # Monthly Fraud Trend
    monthly_fraud_stats = db.session.query(
        db.func.strftime("%Y-%m", InsuranceClaim.claim_date),
        db.func.count(InsuranceClaim.claim_id)
    ).join(FraudPrediction, InsuranceClaim.claim_id == FraudPrediction.claim_id).filter(
        FraudPrediction.predicted_label == "Fraud"
    ).group_by(db.func.strftime("%Y-%m", InsuranceClaim.claim_date)).all()
    
    monthly_fraud_dict = {row[0]: row[1] for row in monthly_fraud_stats if row[0] is not None}
    
    # Merge monthly trends
    combined_trends = []
    for trend in monthly_trend:
        month = trend["month"]
        combined_trends.append({
            "month": month,
            "claims": trend["claims"],
            "fraud": monthly_fraud_dict.get(month, 0)
        })

    # 5. Top Fraud Reasons Extraction
    all_remarks = db.session.query(FraudPrediction.remarks).filter(
        FraudPrediction.remarks.isnot(None),
        FraudPrediction.predicted_label == "Fraud"
    ).all()
    
    reasons_list = []
    for remark in all_remarks:
        # Remarks contain comma-separated explanations, e.g. "Claim is high, Stay is long"
        parts = [p.strip() for p in remark[0].split(".") if p.strip()]
        reasons_list.extend(parts)
        
    reason_counts = Counter(reasons_list).most_common(5)
    top_reasons = [{"reason": item[0], "count": item[1]} for item in reason_counts]

    return {
        "kpis": {
            "total_claims": total_claims,
            "approved_claims": approved_claims,
            "rejected_claims": rejected_claims,
            "fraud_claims": fraud_detected,
            "pending_claims": pending_review,
            "average_claim_amount": round(avg_claim, 2)
        },
        "risk_distribution": risk_distribution,
        "monthly_trend": combined_trends,
        "top_reasons": top_reasons
    }
