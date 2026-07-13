"""
===========================================================
Healthcare Fraud Detection System
Investigation Service
===========================================================

This module compiles the manual review queue for claims flagged as high-risk
by the machine learning models.
"""

from typing import List, Dict, Any
from repositories.prediction_repository import find_high_risk_predictions_with_claims
from constants import STATUS_SUBMITTED, STATUS_UNDER_REVIEW
from utils.logger import logger

def get_investigation_queue_service() -> List[Dict[str, Any]]:
    """
    Fetch and compile high-risk claims currently pending review.
    
    Returns:
        list: Filtered and formatted claim dictionaries with nested predictions.
    """
    logger.info("Compiling investigation queue...")
    
    # Query database via repository
    high_risk_preds = find_high_risk_predictions_with_claims()
    
    claims_list = []
    for pred_data in high_risk_preds:
        claim_data = pred_data.get("claim")
        if claim_data:
            # Handle nested arrays from relation joins
            if isinstance(claim_data, list) and len(claim_data) > 0:
                claim_data = claim_data[0]
                
            if isinstance(claim_data, dict) and claim_data.get("claim_status") in [STATUS_SUBMITTED, STATUS_UNDER_REVIEW]:
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
                claims_list.append(claim_dict)
                
    # Sort queue: newest predictions first
    claims_list.sort(key=lambda x: x.get("prediction", {}).get("prediction_date", ""), reverse=True)
    
    return claims_list
