import sys
import os
from pathlib import Path

# Dynamically append the ML directory (sibling of backend) to python's import path
BASE_DIR = Path(__file__).resolve().parent.parent
ML_DIR = os.path.abspath(BASE_DIR / ".." / "ml")
if ML_DIR not in sys.path:
    sys.path.append(ML_DIR)

from predict import predict_claim
from models import FraudPrediction
from repositories.prediction_repository import save_prediction as db_save_prediction
from utils.logger import logger

def run_claim_prediction(claim_id: int, claim_payload: dict) -> dict:
    """
    Execute machine learning prediction for an insurance claim,
    save the prediction outputs to the database, and return the scored result.
    """
    logger.info(f"Executing fraud prediction for claim ID: {claim_id}")
    
    try:
        # Run ML model inference
        result = predict_claim(claim_payload)
        
        # Construct FraudPrediction SQLAlchemy instance
        prediction = FraudPrediction(
            claim_id=claim_id,
            predicted_label=result["predicted_label"],
            fraud_probability=result["fraud_probability"],
            risk_level=result["risk_level"],
            model_version=result["model_version"],
            remarks=", ".join(result["reasons"])
        )
        
        # Save to database (prediction_repository)
        db_save_prediction(prediction)
        
        logger.info(
            f"Prediction saved for claim ID {claim_id}: label={result['predicted_label']}, "
            f"probability={result['fraud_probability']}, risk_level={result['risk_level']}"
        )
        
        return result
        
    except Exception as e:
        logger.exception(f"Error during claim prediction scoring: {e}")
        # Return fallback safe evaluation if model fails to prevent app crash
        return {
            "predicted_label": "Not Fraud",
            "fraud_probability": 0.0,
            "risk_level": "Low",
            "confidence": 1.0,
            "reasons": ["Fallback: Model failed to execute prediction"],
            "model_version": "fallback"
        }
