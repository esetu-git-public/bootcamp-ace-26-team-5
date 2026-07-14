import os
from flask import Blueprint
from flask_jwt_extended import jwt_required

from middleware.role_auth import role_required
from utils.response import success_response, error_response
from utils.supabase_client import supabase

reports_bp = Blueprint("reports", __name__)

@reports_bp.route("", methods=["GET"])
@jwt_required()
@role_required("admin")
def generate_reports():
    """
    GET /api/reports
    Compiles detailed analytical reports for export (claims breakdown, fraud rates, and investigation queues).
    Restricted to Admins.
    """
    try:
        # Get admin dashboard summary data
        from services.dashboard_service import get_admin_dashboard_summary
        dash_data = get_admin_dashboard_summary()
        
        # 1. Fetch claims for provider and insurance distributions
        if os.getenv("DB_PROVIDER") == "sqlite":
            from utils.sqlite_client import get_sqlite_conn
            with get_sqlite_conn() as conn:
                rows = conn.execute(
                    """SELECT c.claim_id, c.claim_type, c.incident_description, p.insurance_type 
                       FROM insurance_claims c
                       LEFT JOIN insurance_policies p ON c.policy_id = p.policy_id"""
                ).fetchall()
                claims_list = []
                for r in rows:
                    claims_list.append({
                        "claim_id": r["claim_id"],
                        "claim_type": r["claim_type"],
                        "incident_description": r["incident_description"],
                        "policy": {
                            "insurance_type": r["insurance_type"]
                        }
                    })
        else:
            res_claims = supabase.table("insurance_claims").select(
                "claim_id, claim_type, incident_description, policy:insurance_policies(insurance_type)"
            ).execute()
            claims_list = res_claims.data if res_claims.data else []
        
        # 2. Compile Insurance Distribution
        insurance_counts = {}
        for row in claims_list:
            policy = row.get("policy")
            ins_type = "Health"  # fallback
            if policy:
                if isinstance(policy, list) and len(policy) > 0:
                    ins_type = policy[0].get("insurance_type", "Health")
                elif isinstance(policy, dict):
                    ins_type = policy.get("insurance_type", "Health")
            insurance_counts[ins_type] = insurance_counts.get(ins_type, 0) + 1
            
        insurance_distribution = [
            {"type": k, "claims": v}
            for k, v in insurance_counts.items()
        ]
        
        # 3. Compile Provider Distribution
        provider_counts = {}
        for row in claims_list:
            desc = row.get("incident_description", "")
            claim_type = row.get("claim_type", "Medical")
            provider = "General Hospital"
            if " at " in desc:
                parts = desc.split(" at ")
                if len(parts) > 1:
                    provider = parts[1].split(".")[0].strip()
            else:
                # Fallback based on claim type
                if claim_type == "Medical":
                    provider = "Sunrise General Hospital"
                elif claim_type == "Vehicle":
                    provider = "Auto Care Center"
                else:
                    provider = "Secure Loss Adjusters"
            provider_counts[provider] = provider_counts.get(provider, 0) + 1
            
        provider_distribution = [
            {"provider": k, "claims": v}
            for k, v in provider_counts.items()
        ]
        
        # 4. Construct final response matching dashboard analytics
        reports_data = {
            "kpis": dash_data["kpis"],
            "risk_distribution": dash_data["risk_distribution"],
            "monthly_trend": dash_data["monthly_trend"],
            "provider_distribution": provider_distribution,
            "insurance_distribution": insurance_distribution
        }
        
        return success_response(data=reports_data, message="Export-ready reports generated successfully")
        
    except Exception as e:
        return error_response(
            message=f"Failed to generate export reports: {str(e)}",
            status_code=500
        )
