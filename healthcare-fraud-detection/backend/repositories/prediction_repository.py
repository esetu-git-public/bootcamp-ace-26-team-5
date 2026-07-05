from models import FraudPrediction
from database import db

def find_prediction_by_claim_id(claim_id: int) -> FraudPrediction:
    """
    Find prediction record for a specific claim.
    """
    return FraudPrediction.query.filter_by(claim_id=claim_id).first()


def save_prediction(prediction: FraudPrediction) -> FraudPrediction:
    """
    Save or update a fraud prediction record in the database.
    """
    existing = find_prediction_by_claim_id(prediction.claim_id)
    if existing:
        # Update existing prediction values
        existing.predicted_label = prediction.predicted_label
        existing.fraud_probability = prediction.fraud_probability
        existing.risk_level = prediction.risk_level
        existing.model_version = prediction.model_version
        existing.remarks = prediction.remarks
        db.session.commit()
        return existing
    else:
        db.session.add(prediction)
        db.session.commit()
        return prediction
