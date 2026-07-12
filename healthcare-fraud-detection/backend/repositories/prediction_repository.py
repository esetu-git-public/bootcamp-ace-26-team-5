from models import FraudPrediction
from utils.supabase_client import supabase
from datetime import datetime

def find_prediction_by_claim_id(claim_id: int) -> FraudPrediction:
    """
    Find prediction record for a specific claim.
    """
    try:
        res = supabase.table("fraud_predictions").select("*").eq("claim_id", claim_id).execute()
        if res.data:
            return FraudPrediction.from_dict(res.data[0])
    except Exception as e:
        print(f"Error finding prediction by claim ID: {e}")
    return None


def save_prediction(prediction: FraudPrediction) -> FraudPrediction:
    """
    Save or update a fraud prediction record in the database.
    """
    existing = find_prediction_by_claim_id(prediction.claim_id)
    payload = {
        "claim_id": prediction.claim_id,
        "predicted_label": prediction.predicted_label,
        "fraud_probability": prediction.fraud_probability,
        "risk_level": prediction.risk_level,
        "model_version": prediction.model_version,
        "remarks": prediction.remarks,
        "prediction_date": datetime.utcnow().isoformat()
    }
    
    try:
        if existing:
            # Update existing prediction values
            res = supabase.table("fraud_predictions").update(payload).eq("prediction_id", existing.prediction_id).execute()
            if res.data:
                return FraudPrediction.from_dict(res.data[0])
        else:
            res = supabase.table("fraud_predictions").insert(payload).execute()
            if res.data:
                return FraudPrediction.from_dict(res.data[0])
    except Exception as e:
        print(f"Error saving prediction: {e}")
    return prediction
