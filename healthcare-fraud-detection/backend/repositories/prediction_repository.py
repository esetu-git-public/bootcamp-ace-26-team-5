import os
from models import FraudPrediction
from utils.supabase_client import supabase
from utils.sqlite_client import get_sqlite_conn
from datetime import datetime

def find_prediction_by_claim_id(claim_id: int) -> FraudPrediction:
    """
    Find prediction record for a specific claim.
    """
    if os.getenv("DB_PROVIDER") == "sqlite":
        try:
            with get_sqlite_conn() as conn:
                row = conn.execute("SELECT * FROM fraud_predictions WHERE claim_id = ?", (claim_id,)).fetchone()
                if row:
                    return FraudPrediction.from_dict(dict(row))
        except Exception as e:
            print(f"Error finding SQLite prediction by claim ID: {e}")
        return None

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
        "raw_probability": prediction.raw_probability,
        "business_rule_adjustment": prediction.business_rule_adjustment,
        "risk_level": prediction.risk_level,
        "model_version": prediction.model_version,
        "remarks": prediction.remarks,
        "prediction_date": datetime.utcnow().isoformat()
    }
    
    if os.getenv("DB_PROVIDER") == "sqlite":
        try:
            with get_sqlite_conn() as conn:
                cursor = conn.cursor()
                if existing:
                    cursor.execute(
                        """UPDATE fraud_predictions SET predicted_label = ?, fraud_probability = ?, 
                           raw_probability = ?, business_rule_adjustment = ?,
                           risk_level = ?, model_version = ?, remarks = ?, prediction_date = ? 
                           WHERE prediction_id = ?""",
                        (payload["predicted_label"], payload["fraud_probability"],
                         payload["raw_probability"], payload["business_rule_adjustment"],
                         payload["risk_level"], payload["model_version"], payload["remarks"],
                         payload["prediction_date"], existing.prediction_id)
                    )
                    prediction.prediction_id = existing.prediction_id
                else:
                    cursor.execute(
                        """INSERT INTO fraud_predictions (claim_id, predicted_label, fraud_probability, 
                           raw_probability, business_rule_adjustment, 
                           risk_level, model_version, remarks, prediction_date) 
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        (payload["claim_id"], payload["predicted_label"], payload["fraud_probability"],
                         payload["raw_probability"], payload["business_rule_adjustment"],
                         payload["risk_level"], payload["model_version"], payload["remarks"],
                         payload["prediction_date"])
                    )
                    prediction.prediction_id = cursor.lastrowid
                conn.commit()
                row = conn.execute("SELECT * FROM fraud_predictions WHERE prediction_id = ?", (prediction.prediction_id,)).fetchone()
                if row:
                    return FraudPrediction.from_dict(dict(row))
        except Exception as e:
            print(f"Error saving SQLite prediction: {e}")
        return prediction

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
