import os
from utils.supabase_client import supabase
from utils.sqlite_client import get_sqlite_conn
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
    if os.getenv("DB_PROVIDER") == "sqlite":
        try:
            with get_sqlite_conn() as conn:
                total_claims = conn.execute("SELECT COUNT(*) FROM insurance_claims").fetchone()[0]
                total_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
                total_policies = conn.execute("SELECT COUNT(*) FROM insurance_policies").fetchone()[0]
                approved_claims = conn.execute("SELECT COUNT(*) FROM insurance_claims WHERE claim_status = 'approved'").fetchone()[0]
                rejected_claims = conn.execute("SELECT COUNT(*) FROM insurance_claims WHERE claim_status = 'rejected'").fetchone()[0]
                fraud_detected = conn.execute("SELECT COUNT(*) FROM fraud_predictions WHERE predicted_label = 'Fraud'").fetchone()[0]
                pending_review = conn.execute("SELECT COUNT(*) FROM insurance_claims WHERE claim_status IN ('submitted', 'under_review')").fetchone()[0]
                
                amounts = [row[0] for row in conn.execute("SELECT claim_amount FROM insurance_claims").fetchall()]
                avg_claim = sum(amounts) / len(amounts) if amounts else 0.0
                
                low_count = conn.execute("SELECT COUNT(*) FROM fraud_predictions WHERE risk_level = 'Low'").fetchone()[0]
                med_count = conn.execute("SELECT COUNT(*) FROM fraud_predictions WHERE risk_level = 'Medium'").fetchone()[0]
                high_count = conn.execute("SELECT COUNT(*) FROM fraud_predictions WHERE risk_level = 'High'").fetchone()[0]
                
                risk_distribution = {
                    "Low": low_count,
                    "Medium": med_count,
                    "High": high_count,
                }
                
                claims_by_month = {}
                fraud_by_month = {}
                claims_rows = conn.execute("SELECT claim_id, claim_date FROM insurance_claims").fetchall()
                preds_rows = conn.execute("SELECT claim_id, predicted_label FROM fraud_predictions").fetchall()
                fraud_claim_ids = {p["claim_id"] for p in preds_rows if p["predicted_label"] == "Fraud"}
                
                for claim in claims_rows:
                    c_date = claim["claim_date"]
                    if c_date:
                        month = c_date[:7]
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
                    
                remarks_rows = conn.execute("SELECT remarks FROM fraud_predictions WHERE predicted_label = 'Fraud'").fetchall()
                reasons_list = []
                for row in remarks_rows:
                    remark = row["remarks"]
                    if remark:
                        parts = [p.strip() for p in remark.split(",") if p.strip()]
                        reasons_list.extend(parts)
                reason_counts = Counter(reasons_list).most_common(5)
                top_reasons = [{"reason": item[0], "count": item[1]} for item in reason_counts]
                
                # Fetch recent audit logs
                recent_logs = []
                try:
                    log_rows = conn.execute("""
                        SELECT a.log_id, a.action, a.details, a.timestamp, u.full_name as user_name
                        FROM audit_logs a
                        LEFT JOIN users u ON a.user_id = u.user_id
                        ORDER BY a.timestamp DESC LIMIT 5
                    """).fetchall()
                    recent_logs = [dict(r) for r in log_rows]
                except Exception as log_err:
                    logger.warning(f"Error querying SQLite recent logs: {log_err}")
                
                return {
                    "kpis": {
                        "total_claims": total_claims,
                        "total_users": total_users,
                        "total_policies": total_policies,
                        "approved_claims": approved_claims,
                        "rejected_claims": rejected_claims,
                        "fraud_claims": fraud_detected,
                        "pending_claims": pending_review,
                        "average_claim_amount": round(avg_claim, 2)
                    },
                    "risk_distribution": risk_distribution,
                    "monthly_trend": combined_trends,
                    "top_reasons": top_reasons,
                    "recent_logs": recent_logs
                }
        except Exception as e:
            logger.error(f"Error compiling SQLite admin dashboard: {e}")
            return {
                "kpis": {
                    "total_claims": 0, "total_users": 0, "total_policies": 0,
                    "approved_claims": 0, "rejected_claims": 0, "fraud_claims": 0,
                    "pending_claims": 0, "average_claim_amount": 0.0
                },
                "risk_distribution": {"Low": 0, "Medium": 0, "High": 0},
                "monthly_trend": [],
                "top_reasons": [],
                "recent_logs": []
            }

    try:
        res_total = supabase.table("insurance_claims").select("claim_id", count="exact").execute()
        total_claims = res_total.count if res_total.count is not None else 0
        
        res_users = supabase.table("users").select("user_id", count="exact").execute()
        total_users = res_users.count if res_users.count is not None else 0
        
        res_policies = supabase.table("insurance_policies").select("policy_id", count="exact").execute()
        total_policies = res_policies.count if res_policies.count is not None else 0
        
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

        # Fetch recent audit logs from Supabase
        recent_logs = []
        try:
            res_logs = supabase.table("audit_logs").select("*, user:users(full_name)").order("timestamp", desc=True).limit(5).execute()
            if res_logs.data:
                for row in res_logs.data:
                    user_data = row.get("user") or {}
                    recent_logs.append({
                        "log_id": row.get("log_id"),
                        "action": row.get("action"),
                        "details": row.get("details"),
                        "timestamp": row.get("timestamp"),
                        "user_name": user_data.get("full_name") or "System"
                    })
        except Exception as log_err:
            logger.warning(f"Error querying Supabase recent logs: {log_err}")

        return {
            "kpis": {
                "total_claims": total_claims,
                "total_users": total_users,
                "total_policies": total_policies,
                "approved_claims": approved_claims,
                "rejected_claims": rejected_claims,
                "fraud_claims": fraud_detected,
                "pending_claims": pending_review,
                "average_claim_amount": round(avg_claim, 2)
            },
            "risk_distribution": risk_distribution,
            "monthly_trend": combined_trends,
            "top_reasons": top_reasons,
            "recent_logs": recent_logs
        }
    except Exception as e:
        logger.error(f"Error compiling admin dashboard: {e}")
        return {
            "kpis": {
                "total_claims": 0, "total_users": 0, "total_policies": 0,
                "approved_claims": 0, "rejected_claims": 0, "fraud_claims": 0,
                "pending_claims": 0, "average_claim_amount": 0.0
            },
            "risk_distribution": {"Low": 0, "Medium": 0, "High": 0},
            "monthly_trend": [],
            "top_reasons": [],
            "recent_logs": []
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
    if os.getenv("DB_PROVIDER") == "sqlite":
        try:
            with get_sqlite_conn() as conn:
                pending_review = conn.execute("SELECT COUNT(*) FROM insurance_claims WHERE claim_status IN ('submitted', 'under_review')").fetchone()[0]
                med_count = conn.execute("SELECT COUNT(*) FROM fraud_predictions WHERE risk_level = 'Medium'").fetchone()[0]
                high_count = conn.execute("SELECT COUNT(*) FROM fraud_predictions WHERE risk_level = 'High'").fetchone()[0]
                
                reviewed_claims = 0
                try:
                    reviewed_claims = conn.execute(
                        "SELECT COUNT(*) FROM audit_logs WHERE user_id = ? AND action IN ('CLAIM_APPROVED', 'CLAIM_REJECTED')",
                        (user_id,)
                    ).fetchone()[0]
                except Exception as e:
                    logger.warning(f"SQLite audit logs error: {e}")

                return {
                    "kpis": {
                        "pending_claims": pending_review,
                        "medium_risk_claims": med_count,
                        "high_risk_claims": high_count,
                        "reviewed_claims": reviewed_claims
                    }
                }
        except Exception as e:
            logger.error(f"Error compiling SQLite officer dashboard: {e}")
            return {
                "kpis": {
                    "pending_claims": 0, "medium_risk_claims": 0, "high_risk_claims": 0, "reviewed_claims": 0
                }
            }

    try:
        res_pending = supabase.table("insurance_claims").select("claim_id", count="exact").in_("claim_status", ["submitted", "under_review"]).execute()
        pending_review = res_pending.count if res_pending.count is not None else 0

        res_med = supabase.table("fraud_predictions").select("prediction_id", count="exact").eq("risk_level", "Medium").execute()
        med_count = res_med.count if res_med.count is not None else 0
        
        res_high = supabase.table("fraud_predictions").select("prediction_id", count="exact").eq("risk_level", "High").execute()
        high_count = res_high.count if res_high.count is not None else 0

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
    if os.getenv("DB_PROVIDER") == "sqlite":
        try:
            with get_sqlite_conn() as conn:
                total_claims = conn.execute("SELECT COUNT(*) FROM insurance_claims WHERE submitted_by = ?", (user_id,)).fetchone()[0]
                approved_claims = conn.execute("SELECT COUNT(*) FROM insurance_claims WHERE submitted_by = ? AND claim_status = 'approved'", (user_id,)).fetchone()[0]
                rejected_claims = conn.execute("SELECT COUNT(*) FROM insurance_claims WHERE submitted_by = ? AND claim_status = 'rejected'", (user_id,)).fetchone()[0]
                pending_review = conn.execute("SELECT COUNT(*) FROM insurance_claims WHERE submitted_by = ? AND claim_status IN ('submitted', 'under_review')", (user_id,)).fetchone()[0]

                return {
                    "kpis": {
                        "total_claims": total_claims,
                        "approved_claims": approved_claims,
                        "rejected_claims": rejected_claims,
                        "pending_claims": pending_review
                    }
                }
        except Exception as e:
            logger.error(f"Error compiling SQLite customer dashboard: {e}")
            return {
                "kpis": {
                    "total_claims": 0, "approved_claims": 0, "rejected_claims": 0, "pending_claims": 0
                }
            }

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
