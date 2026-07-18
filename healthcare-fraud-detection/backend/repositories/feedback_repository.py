import os
from models import ModelFeedback
from utils.sqlite_client import get_sqlite_conn
from utils.supabase_client import supabase

def create_feedback(claim_id: int, user_id: int, is_incorrect: bool, actual_label: str, feedback_text: str, model_version: str = "v1.0") -> ModelFeedback:
    """
    Insert a feedback entry for a claim.
    """
    is_inc_val = 1 if is_incorrect else 0

    if os.getenv("DB_PROVIDER") == "sqlite":
        try:
            with get_sqlite_conn() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO model_feedback 
                    (claim_id, user_id, is_incorrect, actual_label, feedback_text, model_version) 
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (claim_id, user_id, is_inc_val, actual_label.strip(), feedback_text.strip(), model_version)
                )
                feedback_id = cursor.lastrowid
                conn.commit()
                row = conn.execute("SELECT * FROM model_feedback WHERE feedback_id = ?", (feedback_id,)).fetchone()
                if row:
                    return ModelFeedback.from_dict(dict(row))
        except Exception as e:
            print(f"Error creating SQLite model feedback: {e}")
        return None

    try:
        data = {
            "claim_id": claim_id,
            "user_id": user_id,
            "is_incorrect": is_incorrect,
            "actual_label": actual_label.strip(),
            "feedback_text": feedback_text.strip(),
            "model_version": model_version
        }
        res = supabase.table("model_feedback").insert(data).execute()
        if res.data:
            return ModelFeedback.from_dict(res.data[0])
    except Exception as e:
        print(f"Error creating model feedback: {e}")
    return None


def get_feedback_by_claim_id(claim_id: int) -> ModelFeedback:
    """
    Retrieve feedback details for a specific claim.
    """
    if os.getenv("DB_PROVIDER") == "sqlite":
        try:
            with get_sqlite_conn() as conn:
                row = conn.execute("SELECT * FROM model_feedback WHERE claim_id = ?", (claim_id,)).fetchone()
                if row:
                    return ModelFeedback.from_dict(dict(row))
        except Exception as e:
            print(f"Error finding SQLite model feedback: {e}")
        return None

    try:
        res = supabase.table("model_feedback").select("*").eq("claim_id", claim_id).execute()
        if res.data:
            return ModelFeedback.from_dict(res.data[0])
    except Exception as e:
        print(f"Error finding model feedback by claim ID: {e}")
    return None


def get_all_feedback() -> list:
    """
    Retrieve all feedback entries joined with claim/prediction details.
    """
    results = []
    if os.getenv("DB_PROVIDER") == "sqlite":
        try:
            with get_sqlite_conn() as conn:
                rows = conn.execute(
                    """
                    SELECT mf.*, fp.predicted_label, fp.risk_level, c.claim_number, u.full_name as user_name
                    FROM model_feedback mf 
                    JOIN insurance_claims c ON mf.claim_id = c.claim_id 
                    LEFT JOIN fraud_predictions fp ON c.claim_id = fp.claim_id
                    LEFT JOIN users u ON mf.user_id = u.user_id
                    ORDER BY mf.created_at DESC
                    """
                ).fetchall()
                for r in rows:
                    item = dict(r)
                    item["is_incorrect"] = bool(item["is_incorrect"])
                    results.append(item)
        except Exception as e:
            print(f"Error listing SQLite model feedback: {e}")
        return results

    try:
        # For Supabase, fetch feedback, claims and predictions, then combine client-side
        res_fb = supabase.table("model_feedback").select("*").order("created_at", desc=True).execute()
        if res_fb.data:
            fb_list = res_fb.data
            claim_ids = [f["claim_id"] for f in fb_list]
            user_ids = list(set([f["user_id"] for f in fb_list if f["user_id"]]))
            
            claims_res = supabase.table("insurance_claims").select("claim_id, claim_number").in_("claim_id", claim_ids).execute()
            preds_res = supabase.table("fraud_predictions").select("claim_id, predicted_label, risk_level").in_("claim_id", claim_ids).execute()
            users_res = supabase.table("users").select("user_id, full_name").in_("user_id", user_ids).execute()
            
            claims_map = {c["claim_id"]: c for c in claims_res.data} if claims_res.data else {}
            preds_map = {p["claim_id"]: p for p in preds_res.data} if preds_res.data else {}
            users_map = {u["user_id"]: u for u in users_res.data} if users_res.data else {}
            
            for fb in fb_list:
                cid = fb["claim_id"]
                uid = fb["user_id"]
                fb["claim_number"] = claims_map.get(cid, {}).get("claim_number", f"CLM-{cid}")
                fb["predicted_label"] = preds_map.get(cid, {}).get("predicted_label", "Unknown")
                fb["risk_level"] = preds_map.get(cid, {}).get("risk_level", "Unknown")
                fb["user_name"] = users_map.get(uid, {}).get("full_name", "Unknown")
                results.append(fb)
    except Exception as e:
        print(f"Error listing model feedback: {e}")
    return results


def get_feedback_stats() -> dict:
    """
    Get aggregated model failure and performance metrics.
    """
    total_predictions = 0
    disagreements = 0
    false_positives = 0
    false_negatives = 0
    label_distribution = {"Fraud": 0, "Not Fraud": 0}

    if os.getenv("DB_PROVIDER") == "sqlite":
        try:
            with get_sqlite_conn() as conn:
                total_predictions = conn.execute("SELECT COUNT(*) FROM fraud_predictions").fetchone()[0]
                disagreements = conn.execute("SELECT COUNT(*) FROM model_feedback WHERE is_incorrect = 1").fetchone()[0]
                
                # False Positives: predicted Fraud, user says Not Fraud
                false_positives = conn.execute(
                    """
                    SELECT COUNT(*) FROM model_feedback mf
                    JOIN fraud_predictions fp ON mf.claim_id = fp.claim_id
                    WHERE mf.is_incorrect = 1 AND fp.predicted_label = 'Fraud' AND mf.actual_label = 'Not Fraud'
                    """
                ).fetchone()[0]
                
                # False Negatives: predicted Not Fraud, user says Fraud
                false_negatives = conn.execute(
                    """
                    SELECT COUNT(*) FROM model_feedback mf
                    JOIN fraud_predictions fp ON mf.claim_id = fp.claim_id
                    WHERE mf.is_incorrect = 1 AND fp.predicted_label = 'Not Fraud' AND mf.actual_label = 'Fraud'
                    """
                ).fetchone()[0]

                # Label distribution for disagreements
                rows = conn.execute(
                    "SELECT actual_label, COUNT(*) FROM model_feedback WHERE is_incorrect = 1 GROUP BY actual_label"
                ).fetchall()
                for r in rows:
                    lbl = r[0]
                    cnt = r[1]
                    if lbl in label_distribution:
                        label_distribution[lbl] = cnt
        except Exception as e:
            print(f"Error querying SQLite feedback stats: {e}")
    else:
        try:
            res_total = supabase.table("fraud_predictions").select("prediction_id", count="exact").execute()
            total_predictions = res_total.count if res_total.count is not None else 0

            res_dis = supabase.table("model_feedback").select("feedback_id", count="exact").eq("is_incorrect", True).execute()
            disagreements = res_dis.count if res_dis.count is not None else 0

            # Fetch list of disagreements to calculate false positive/negative client-side
            res_fb = supabase.table("model_feedback").select("claim_id, actual_label").eq("is_incorrect", True).execute()
            if res_fb.data:
                fb_list = res_fb.data
                claim_ids = [f["claim_id"] for f in fb_list]
                
                res_preds = supabase.table("fraud_predictions").select("claim_id, predicted_label").in_("claim_id", claim_ids).execute()
                preds_map = {p["claim_id"]: p["predicted_label"] for p in res_preds.data} if res_preds.data else {}
                
                for fb in fb_list:
                    cid = fb["claim_id"]
                    act = fb["actual_label"]
                    pred = preds_map.get(cid, "Unknown")
                    
                    if act == "Not Fraud":
                        label_distribution["Not Fraud"] += 1
                        if pred == "Fraud":
                            false_positives += 1
                    elif act == "Fraud":
                        label_distribution["Fraud"] += 1
                        if pred == "Not Fraud":
                            false_negatives += 1
        except Exception as e:
            print(f"Error querying feedback stats: {e}")

    disagreement_rate = (disagreements / total_predictions) if total_predictions > 0 else 0.0

    # Use the model's training validation accuracy as the baseline (from model_metadata.json)
    # instead of showing a misleading 100% when no officer has flagged any predictions yet.
    MODEL_BASELINE_ACCURACY = 0.932  # 93.2% from model_metadata.json

    if disagreements == 0:
        # No officer feedback yet — display the model's validated training accuracy
        accuracy = MODEL_BASELINE_ACCURACY
    else:
        # Blend: weight live feedback accuracy against the training baseline
        live_accuracy = 1.0 - disagreement_rate
        accuracy = min(live_accuracy, MODEL_BASELINE_ACCURACY)

    return {
        "totalPredictions": total_predictions,
        "disagreements": disagreements,
        "disagreementRate": round(disagreement_rate * 100, 1),
        "accuracy": round(accuracy * 100, 1),
        "falsePositives": false_positives,
        "falseNegatives": false_negatives,
        "labelDistribution": [
            {"name": "Flagged Fraud (Missed by Model)", "value": label_distribution["Fraud"]},
            {"name": "Flagged Genuine (False Alarm)", "value": label_distribution["Not Fraud"]}
        ]
    }

