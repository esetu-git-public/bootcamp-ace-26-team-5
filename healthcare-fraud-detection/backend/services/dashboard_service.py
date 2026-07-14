from utils.supabase_client import supabase
from collections import Counter
from utils.logger import logger

def get_dashboard(role: str, user_id: int) -> dict:
    """
    Unified Dashboard Service compiles specific metrics depending on user role and ID.
    Gracefully handles table missing errors (PGRST205) for audit_logs.
    """
    role = (role or "").strip().lower()
    
    if role == "admin":
        return get_admin_dashboard_summary()
    elif role == "employee":
        return get_officer_dashboard_summary(user_id)
    else:
        return get_customer_dashboard_summary(user_id)


def get_admin_dashboard_summary() -> dict:
    """
    Compile full KPIs and Recharts analytics for Admin.
    """
    try:
        res_total = supabase.table("insurance_claims").select("claim_id", count="exact").execute()
        total_claims = res_total.count if res_total.count is not None else 0
        
        res_approved = supabase.table("insurance_claims").select("claim_id", count="exact").eq("claim_status", "approved").execute()
        approved_claims = res_approved.count if res_approved.count is not None else 0
        
        res_rejected = supabase.table("insurance_claims").select("claim_id", count="exact").eq("claim_status", "rejected").execute()
        rejected_claims = res_rejected.count if res_rejected.count is not None else 0
        
        res_fraud = supabase.table("fraud_predictions").select("prediction_id", count="exact").eq("predicted_label", "Fraud").execute()
        fraud_detected = res_fraud.count if res_fraud.count is not None else 0
        
        res_pending = supabase.table("insurance_claims").select("claim_id", count="exact").in_("claim_status", ["submitted", "under_review"]).execute()
        pending_review = res_pending.count if res_pending.count is not None else 0

        # Averages
        res_amounts = supabase.table("insurance_claims").select("claim_amount").execute()
        amounts = [float(row["claim_amount"]) for row in res_amounts.data] if res_amounts.data else []
        avg_claim = sum(amounts) / len(amounts) if amounts else 0.0
        
        # Risk Distribution
        res_low = supabase.table("fraud_predictions").select("prediction_id", count="exact").eq("risk_level", "Low").execute()
        low_count = res_low.count if res_low.count is not None else 0
        
        res_med = supabase.table("fraud_predictions").select("prediction_id", count="exact").eq("risk_level", "Medium").execute()
        med_count = res_med.count if res_med.count is not None else 0
        
        res_high = supabase.table("fraud_predictions").select("prediction_id", count="exact").eq("risk_level", "High").execute()
        high_count = res_high.count if res_high.count is not None else 0
        
        risk_distribution = {
            "Low": low_count,
            "Medium": med_count,
            "High": high_count,
        }

        # Monthly Trend (last 6 months)
        res_claims = supabase.table("insurance_claims").select("claim_id, claim_date").execute()
        res_preds = supabase.table("fraud_predictions").select("claim_id, predicted_label").execute()
        
        fraud_claim_ids = {p["claim_id"] for p in res_preds.data if p["predicted_label"] == "Fraud"} if res_preds.data else set()
        
        claims_by_month = {}
        fraud_by_month = {}
        if res_claims.data:
            for claim in res_claims.data:
                c_date = claim.get("claim_date")
                if c_date:
                    month = c_date[:7]  # YYYY-MM
                    claims_by_month[month] = claims_by_month.get(month, 0) + 1
                    if claim["claim_id"] in fraud_claim_ids:
                        fraud_by_month[month] = fraud_by_month.get(month, 0) + 1
                        
        sorted_months = sorted(list(claims_by_month.keys()))
        combined_trends = []
        for month in sorted_months:
            combined_trends.append({
                "month": month,
                "claims": claims_by_month[month],
                "fraud": fraud_by_month.get(month, 0)
            })

        # Top Fraud Reasons
        res_remarks = supabase.table("fraud_predictions").select("remarks").eq("predicted_label", "Fraud").execute()
        reasons_list = []
        if res_remarks.data:
            for row in res_remarks.data:
                remark = row.get("remarks")
                if remark:
                    parts = [p.strip() for p in remark.split(",") if p.strip()]
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
    except Exception as e:
        logger.error(f"Error compiling admin dashboard: {e}")
        return {
            "kpis": {
                "total_claims": 0, "approved_claims": 0, "rejected_claims": 0,
                "fraud_claims": 0, "pending_claims": 0, "average_claim_amount": 0.0
            },
            "risk_distribution": {"Low": 0, "Medium": 0, "High": 0},
            "monthly_trend": [],
            "top_reasons": []
        }


def get_officer_dashboard_summary(user_id: int) -> dict:
    """
    Compile KPIs for the Claims Officer queue dashboard.
    """
    try:
        # Total Claims in review
        res_pending = supabase.table("insurance_claims").select("claim_id", count="exact").in_("claim_status", ["submitted", "under_review"]).execute()
        pending_review = res_pending.count if res_pending.count is not None else 0

        # Pending High and Medium risk claims
        res_med = supabase.table("fraud_predictions").select("prediction_id", count="exact").eq("risk_level", "Medium").execute()
        med_count = res_med.count if res_med.count is not None else 0
        
        res_high = supabase.table("fraud_predictions").select("prediction_id", count="exact").eq("risk_level", "High").execute()
        high_count = res_high.count if res_high.count is not None else 0

        # Reviewed claims by this officer (graceful fallback if audit_logs table missing)
        reviewed_claims = 0
        try:
            res_logs = supabase.table("audit_logs").select("log_id", count="exact").eq("user_id", user_id).in_("action", ["CLAIM_APPROVED", "CLAIM_REJECTED"]).execute()
            reviewed_claims = res_logs.count if res_logs.count is not None else 0
        except Exception as db_err:
            logger.warning(f"Graceful degradation: audit_logs table missing during officer dashboard fetch: {db_err}")

        return {
            "kpis": {
                "pending_claims": pending_review,
                "medium_risk_claims": med_count,
                "high_risk_claims": high_count,
                "reviewed_claims": reviewed_claims
            }
        }
    except Exception as e:
        logger.error(f"Error compiling officer dashboard: {e}")
        return {
            "kpis": {
                "pending_claims": 0, "medium_risk_claims": 0, "high_risk_claims": 0, "reviewed_claims": 0
            }
        }


def get_customer_dashboard_summary(user_id: int) -> dict:
    """
    Compile claim metrics isolated for a Customer.
    """
    try:
        res_total = supabase.table("insurance_claims").select("claim_id", count="exact").eq("submitted_by", user_id).execute()
        total_claims = res_total.count if res_total.count is not None else 0
        
        res_approved = supabase.table("insurance_claims").select("claim_id", count="exact").eq("submitted_by", user_id).eq("claim_status", "approved").execute()
        approved_claims = res_approved.count if res_approved.count is not None else 0
        
        res_rejected = supabase.table("insurance_claims").select("claim_id", count="exact").eq("submitted_by", user_id).eq("claim_status", "rejected").execute()
        rejected_claims = res_rejected.count if res_rejected.count is not None else 0
        
        res_pending = supabase.table("insurance_claims").select("claim_id", count="exact").eq("submitted_by", user_id).in_("claim_status", ["submitted", "under_review"]).execute()
        pending_review = res_pending.count if res_pending.count is not None else 0

        return {
            "kpis": {
                "total_claims": total_claims,
                "approved_claims": approved_claims,
                "rejected_claims": rejected_claims,
                "pending_claims": pending_review
            }
        }
    except Exception as e:
        logger.error(f"Error compiling customer dashboard: {e}")
        return {
            "kpis": {
                "total_claims": 0, "approved_claims": 0, "rejected_claims": 0, "pending_claims": 0
            }
        }
