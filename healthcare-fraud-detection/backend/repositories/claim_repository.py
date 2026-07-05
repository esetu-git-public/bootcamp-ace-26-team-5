from models import InsuranceClaim
from database import db

def find_claim_by_id(claim_id: int) -> InsuranceClaim:
    """
    Retrieve an insurance claim by its unique ID.
    """
    return db.session.get(InsuranceClaim, claim_id)


def find_claim_by_number(claim_number: str) -> InsuranceClaim:
    """
    Retrieve an insurance claim by its unique claim number.
    """
    if not claim_number:
        return None
    return InsuranceClaim.query.filter_by(claim_number=claim_number.strip()).first()


def save_claim(claim: InsuranceClaim) -> InsuranceClaim:
    """
    Save or insert an insurance claim into the database.
    """
    db.session.add(claim)
    db.session.commit()
    return claim


def get_paginated_claims(filters: dict = None, sort_by: str = "created_at", order: str = "desc", page: int = 1, per_page: int = 10):
    """
    Query, filter, sort, and paginate claim records.
    """
    query = InsuranceClaim.query

    if filters:
        if "claim_status" in filters and filters["claim_status"]:
            query = query.filter_by(claim_status=filters["claim_status"])
        if "claim_type" in filters and filters["claim_type"]:
            query = query.filter(InsuranceClaim.claim_type.ilike(f"%{filters['claim_type']}%"))
        if "search_query" in filters and filters["search_query"]:
            search = f"%{filters['search_query']}%"
            query = query.filter(
                (InsuranceClaim.claim_number.ilike(search)) |
                (InsuranceClaim.incident_location.ilike(search))
            )

    # Sort
    sort_column = getattr(InsuranceClaim, sort_by, InsuranceClaim.created_at)
    if order.lower() == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    # Paginate
    return query.paginate(page=page, per_page=per_page, error_out=False)


def delete_claim(claim_id: int) -> bool:
    """
    Delete a claim from the database.
    """
    claim = find_claim_by_id(claim_id)
    if not claim:
        return False
    db.session.delete(claim)
    db.session.commit()
    return True
