import os
from models import InsuranceClaim, FraudPrediction
from utils.supabase_client import supabase
from utils.sqlite_client import get_sqlite_conn

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
    if os.getenv("DB_PROVIDER") == "sqlite":
        try:
            with get_sqlite_conn() as conn:
                claim_row = conn.execute("SELECT * FROM insurance_claims WHERE claim_id = ?", (claim_id,)).fetchone()
                if not claim_row:
                    return None
                claim_data = dict(claim_row)
                
                # Fetch prediction
                pred_row = conn.execute("SELECT * FROM fraud_predictions WHERE claim_id = ?", (claim_id,)).fetchone()
                prediction_obj = FraudPrediction.from_dict(dict(pred_row)) if pred_row else None
                
                # Fetch policy and policyholder details
                policy_row = conn.execute("SELECT * FROM insurance_policies WHERE policy_id = ?", (claim_data["policy_id"],)).fetchone()
                policy_embedded = None
                if policy_row:
                    policy_embedded = dict(policy_row)
                    ph_row = conn.execute("SELECT * FROM policyholders WHERE policyholder_id = ?", (policy_embedded["policyholder_id"],)).fetchone()
                    policy_embedded["policyholder"] = dict(ph_row) if ph_row else None
                
                claim = InsuranceClaim.from_dict(claim_data)
                claim.prediction = prediction_obj
                claim.policy_embedded = policy_embedded
                return claim
        except Exception as e:
            print(f"Error finding SQLite claim by ID: {e}")
        return None

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
    if os.getenv("DB_PROVIDER") == "sqlite":
        try:
            with get_sqlite_conn() as conn:
                claim_row = conn.execute("SELECT * FROM insurance_claims WHERE claim_number = ?", (claim_number.strip(),)).fetchone()
                if not claim_row:
                    return None
                claim_data = dict(claim_row)
                
                # Fetch prediction
                pred_row = conn.execute("SELECT * FROM fraud_predictions WHERE claim_id = ?", (claim_data["claim_id"],)).fetchone()
                prediction_obj = FraudPrediction.from_dict(dict(pred_row)) if pred_row else None
                
                # Fetch policy and policyholder
                policy_row = conn.execute("SELECT * FROM insurance_policies WHERE policy_id = ?", (claim_data["policy_id"],)).fetchone()
                policy_embedded = None
                if policy_row:
                    policy_embedded = dict(policy_row)
                    ph_row = conn.execute("SELECT * FROM policyholders WHERE policyholder_id = ?", (policy_embedded["policyholder_id"],)).fetchone()
                    policy_embedded["policyholder"] = dict(ph_row) if ph_row else None
                
                claim = InsuranceClaim.from_dict(claim_data)
                claim.prediction = prediction_obj
                claim.policy_embedded = policy_embedded
                return claim
        except Exception as e:
            print(f"Error finding SQLite claim by number: {e}")
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
    Save or insert an insurance claim into database.
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
    
    if os.getenv("DB_PROVIDER") == "sqlite":
        try:
            with get_sqlite_conn() as conn:
                cursor = conn.cursor()
                if claim.claim_id:
                    cursor.execute(
                        """UPDATE insurance_claims SET claim_number = ?, policy_id = ?, claim_date = ?, 
                           incident_date = ?, claim_type = ?, claim_amount = ?, incident_location = ?, 
                           incident_description = ?, police_report_available = ?, witnesses_count = ?, 
                           claim_status = ?, submitted_by = ? WHERE claim_id = ?""",
                        (payload["claim_number"], payload["policy_id"], payload["claim_date"],
                         payload["incident_date"], payload["claim_type"], payload["claim_amount"],
                         payload["incident_location"], payload["incident_description"],
                         payload["police_report_available"], payload["witnesses_count"],
                         payload["claim_status"], payload["submitted_by"], claim.claim_id)
                    )
                else:
                    cursor.execute(
                        """INSERT INTO insurance_claims (claim_number, policy_id, claim_date, incident_date, 
                           claim_type, claim_amount, incident_location, incident_description, 
                           police_report_available, witnesses_count, claim_status, submitted_by) 
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        (payload["claim_number"], payload["policy_id"], payload["claim_date"],
                         payload["incident_date"], payload["claim_type"], payload["claim_amount"],
                         payload["incident_location"], payload["incident_description"],
                         payload["police_report_available"], payload["witnesses_count"],
                         payload["claim_status"], payload["submitted_by"])
                    )
                    claim.claim_id = cursor.lastrowid
                conn.commit()
                return find_claim_by_id(claim.claim_id)
        except Exception as e:
            print(f"Error saving SQLite claim: {e}")
        return claim

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
    Query, filter, sort, and paginate claim records from database.
    """
    if os.getenv("DB_PROVIDER") == "sqlite":
        try:
            base_query = "SELECT c.* FROM insurance_claims c"
            where_clauses = []
            params = []
            
            if filters:
                if "submitted_by" in filters and filters["submitted_by"] is not None:
                    where_clauses.append("c.submitted_by = ?")
                    params.append(filters["submitted_by"])
                if "claim_status" in filters and filters["claim_status"]:
                    where_clauses.append("c.claim_status = ?")
                    params.append(filters["claim_status"])
                if "claim_type" in filters and filters["claim_type"]:
                    where_clauses.append("c.claim_type LIKE ?")
                    params.append(f"%{filters['claim_type']}%")
                if "search_query" in filters and filters["search_query"]:
                    where_clauses.append("(c.claim_number LIKE ? OR c.incident_location LIKE ?)")
                    term = f"%{filters['search_query']}%"
                    params.append(term)
                    params.append(term)
            
            where_sql = ""
            if where_clauses:
                where_sql = " WHERE " + " AND ".join(where_clauses)
                
            count_query = f"SELECT COUNT(*) as count FROM insurance_claims c{where_sql}"
            with get_sqlite_conn() as conn:
                count_row = conn.execute(count_query, params).fetchone()
                total = count_row["count"] if count_row else 0
                
                allowed_sort = {"created_at", "claim_amount", "claim_date", "claim_status"}
                sort_col = "created_at"
                if sort_by in allowed_sort:
                    sort_col = sort_by
                sort_order = "DESC" if order.lower() == "desc" else "ASC"
                
                limit = per_page
                offset = (page - 1) * per_page
                
                data_query = f"{base_query}{where_sql} ORDER BY c.{sort_col} {sort_order} LIMIT ? OFFSET ?"
                rows = conn.execute(data_query, params + [limit, offset]).fetchall()
                
                items = []
                for r in rows:
                    claim_data = dict(r)
                    claim_id = claim_data["claim_id"]
                    
                    pred_row = conn.execute("SELECT * FROM fraud_predictions WHERE claim_id = ?", (claim_id,)).fetchone()
                    prediction_obj = FraudPrediction.from_dict(dict(pred_row)) if pred_row else None
                    
                    policy_row = conn.execute("SELECT * FROM insurance_policies WHERE policy_id = ?", (claim_data["policy_id"],)).fetchone()
                    policy_embedded = None
                    if policy_row:
                        policy_embedded = dict(policy_row)
                        ph_row = conn.execute("SELECT * FROM policyholders WHERE policyholder_id = ?", (policy_embedded["policyholder_id"],)).fetchone()
                        policy_embedded["policyholder"] = dict(ph_row) if ph_row else None
                    
                    claim = InsuranceClaim.from_dict(claim_data)
                    claim.prediction = prediction_obj
                    claim.policy_embedded = policy_embedded
                    items.append(claim)
                    
                return SupabasePagination(items, total, page, per_page)
        except Exception as e:
            print(f"Error fetching SQLite paginated claims: {e}")
            return SupabasePagination([], 0, page, per_page)

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
    Delete a claim from database.
    """
    if os.getenv("DB_PROVIDER") == "sqlite":
        try:
            with get_sqlite_conn() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM insurance_claims WHERE claim_id = ?", (claim_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting SQLite claim: {e}")
            return False

    try:
        res = supabase.table("insurance_claims").delete().eq("claim_id", claim_id).execute()
        return len(res.data) > 0
    except Exception as e:
        print(f"Error deleting claim: {e}")
        return False
