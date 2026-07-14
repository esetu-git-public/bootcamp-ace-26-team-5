"""
===========================================================
Healthcare Fraud Detection System
Report Service
===========================================================

This module compiles claims summaries, fraud distributions, and manual review
statistics for analytical exports.
"""

from typing import Dict, List, Any
from repositories.claim_repository import get_claim_statuses_and_amounts, get_claims_by_status_with_predictions
from repositories.prediction_repository import find_predictions_by_label_with_claims
from constants import LABEL_FRAUD, STATUS_UNDER_REVIEW
from utils.logger import logger

def compile_analytical_reports() -> Dict[str, Any]:
    """
    Compile reports on claim statuses, flagged fraud, and current reviews.
    
    Returns:
        dict: Analytics data structures matching the exports API schema.
    """
    logger.info("Compiling analytics reports...")
    
    # 1. Claims Report Status aggregates
    claims_raw = get_claim_statuses_and_amounts()
    claims_by_status = {}
    for row in claims_raw:
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

    # 2. Fraud Flagged predictions list
    fraud_preds = find_predictions_by_label_with_claims(LABEL_FRAUD)
    # Sort predictions by probability descending
    fraud_preds.sort(key=lambda x: x.get("fraud_probability", 0.0), reverse=True)
    
    fraud_report = []
    for row in fraud_preds:
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

    # 3. Claims under review for manual queue report
    review_claims = get_claims_by_status_with_predictions(STATUS_UNDER_REVIEW)
    investigation_report = []
    for claim in review_claims:
        risk_level = "Low"
        if claim.prediction:
            risk_level = claim.prediction.risk_level
            
        submitted_at_str = claim.created_at
        if hasattr(claim.created_at, "isoformat"):
            submitted_at_str = claim.created_at.isoformat()
            
        investigation_report.append({
            "claim_number": claim.claim_number,
            "claim_amount": claim.claim_amount,
            "claim_type": claim.claim_type,
            "risk_level": risk_level,
            "submitted_at": submitted_at_str
        })
        
    return {
        "claims_report": claims_report,
        "fraud_report": fraud_report,
        "investigation_report": investigation_report
    }
