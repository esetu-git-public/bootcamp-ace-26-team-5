from models import InsuranceClaim, FraudPrediction
from utils.supabase_client import supabase

class SupabasePagination:
    def __init__(self, items, total, page, per_page):
        self.items = items
        self.total = total
        self.page = page
        self.per_page = per_page
        self.pages = (total + per_page - 1) // per_page if per_page > 0 else 0
        self.has_next = page < self.pages
        self.has_prev = page > 1

def find_claim_by_id(claim_id: int) -> InsuranceClaim:
    """
    Retrieve an insurance claim by its unique ID, fetching its nested prediction and policy/policyholder relation.
    """
    try:
        res = supabase.table("insurance_claims").select(
            "*, prediction:fraud_predictions(*), policy:insurance_policies(*, policyholder:policyholders(*))"
        ).eq("claim_id", claim_id).execute()
        if res.data:
            claim_data = res.data[0]
            predictions = claim_data.get("prediction") or claim_data.get("fraud_predictions")
            prediction_obj = None
            if predictions:
                if isinstance(predictions, list) and len(predictions) > 0:
                    prediction_obj = FraudPrediction.from_dict(predictions[0])
                elif isinstance(predictions, dict):
                    prediction_obj = FraudPrediction.from_dict(predictions)
            
            claim = InsuranceClaim.from_dict(claim_data)
            claim.prediction = prediction_obj
            # Embed policy/policyholder dict details directly onto the object
            claim.policy_embedded = claim_data.get("policy")
            return claim
    except Exception as e:
        print(f"Error finding claim by ID: {e}")
    return None


def find_claim_by_number(claim_number: str) -> InsuranceClaim:
    """
    Retrieve an insurance claim by its unique claim number, fetching nested relation details.
    """
    if not claim_number:
        return None
    try:
        res = supabase.table("insurance_claims").select(
            "*, prediction:fraud_predictions(*), policy:insurance_policies(*, policyholder:policyholders(*))"
        ).eq("claim_number", claim_number.strip()).execute()
        if res.data:
            claim_data = res.data[0]
            predictions = claim_data.get("prediction") or claim_data.get("fraud_predictions")
            prediction_obj = None
            if predictions:
                if isinstance(predictions, list) and len(predictions) > 0:
                    prediction_obj = FraudPrediction.from_dict(predictions[0])
                elif isinstance(predictions, dict):
                    prediction_obj = FraudPrediction.from_dict(predictions)
            
            claim = InsuranceClaim.from_dict(claim_data)
            claim.prediction = prediction_obj
            claim.policy_embedded = claim_data.get("policy")
            return claim
    except Exception as e:
        print(f"Error finding claim by number: {e}")
    return None


def save_claim(claim: InsuranceClaim) -> InsuranceClaim:
    """
    Save or insert an insurance claim into Supabase.
    """
    payload = {
        "claim_number": claim.claim_number.strip(),
        "policy_id": claim.policy_id,
        "claim_date": claim.claim_date.isoformat() if hasattr(claim.claim_date, "isoformat") else claim.claim_date,
        "incident_date": claim.incident_date.isoformat() if hasattr(claim.incident_date, "isoformat") else claim.incident_date,
        "claim_type": claim.claim_type,
        "claim_amount": float(claim.claim_amount),
        "incident_location": claim.incident_location,
        "incident_description": claim.incident_description,
        "police_report_available": int(claim.police_report_available),
        "witnesses_count": int(claim.witnesses_count),
        "claim_status": claim.claim_status,
        "submitted_by": claim.submitted_by
    }
    
    try:
        if claim.claim_id:
            res = supabase.table("insurance_claims").update(payload).eq("claim_id", claim.claim_id).execute()
        else:
            res = supabase.table("insurance_claims").insert(payload).execute()
            
        if res.data:
            saved_claim = InsuranceClaim.from_dict(res.data[0])
            saved_claim.prediction = claim.prediction
            return saved_claim
    except Exception as e:
        print(f"Error saving claim: {e}")
    return claim


def get_paginated_claims(filters: dict = None, sort_by: str = "created_at", order: str = "desc", page: int = 1, per_page: int = 10):
    """
    Query, filter, sort, and paginate claim records from Supabase.
    """
    try:
        query = supabase.table("insurance_claims").select(
            "*, prediction:fraud_predictions(*), policy:insurance_policies(*, policyholder:policyholders(*))",
            count="exact"
        )
        
        if filters:
            if "submitted_by" in filters and filters["submitted_by"] is not None:
                query = query.eq("submitted_by", filters["submitted_by"])
            if "claim_status" in filters and filters["claim_status"]:
                query = query.eq("claim_status", filters["claim_status"])
            if "claim_type" in filters and filters["claim_type"]:
                query = query.ilike("claim_type", f"%{filters['claim_type']}%")
            if "search_query" in filters and filters["search_query"]:
                search = f"%{filters['search_query']}%"
                query = query.or_(f"claim_number.ilike.{search},incident_location.ilike.{search}")

        if sort_by == "created_at":
            sort_by = "created_at"
            
        query = query.order(sort_by, desc=(order.lower() == "desc"))
        
        start = (page - 1) * per_page
        end = start + per_page - 1
        
        res = query.range(start, end).execute()
        
        items = []
        for claim_data in res.data:
            predictions = claim_data.get("prediction") or claim_data.get("fraud_predictions")
            prediction_obj = None
            if predictions:
                if isinstance(predictions, list) and len(predictions) > 0:
                    prediction_obj = FraudPrediction.from_dict(predictions[0])
                elif isinstance(predictions, dict):
                    prediction_obj = FraudPrediction.from_dict(predictions)
            
            claim = InsuranceClaim.from_dict(claim_data)
            claim.prediction = prediction_obj
            claim.policy_embedded = claim_data.get("policy")
            items.append(claim)
            
        total = res.count if res.count is not None else len(items)
        return SupabasePagination(items, total, page, per_page)
    except Exception as e:
        print(f"Error fetching paginated claims: {e}")
        return SupabasePagination([], 0, page, per_page)


def delete_claim(claim_id: int) -> bool:
    """
    Delete a claim from Supabase.
    """
    try:
        res = supabase.table("insurance_claims").delete().eq("claim_id", claim_id).execute()
        return len(res.data) > 0
    except Exception as e:
        print(f"Error deleting claim: {e}")
        return False
