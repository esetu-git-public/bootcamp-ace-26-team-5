from datetime import datetime

def validate_claim_payload(data: dict) -> tuple[bool, str]:
    """
    Validate claims input data. Supports standard database format and frontend form format.
    Returns (is_valid, error_message).
    """
    if not data:
        return False, "Request payload is empty"

    # 1. Check if it's the frontend form format
    if "patientName" in data or "claimAmount" in data:
        patient_name = data.get("patientName")
        claim_amount = data.get("claimAmount")
        
        if not patient_name or not patient_name.strip():
            return False, "Patient name is required"
            
        if claim_amount is None:
            return False, "Claim amount is required"
            
        try:
            amount = float(claim_amount)
            if amount <= 0:
                return False, "Claim amount must be greater than zero"
        except ValueError:
            return False, "Claim amount must be a valid number"
            
        return True, ""

    # 2. Check if it's the standard database API format
    claim_number = data.get("claim_number")
    claim_amount = data.get("claim_amount")
    policy_id = data.get("policy_id")
    claim_date = data.get("claim_date")

    if not claim_number or not claim_number.strip():
        return False, "Claim number is required"

    if claim_amount is None:
        return False, "Claim amount is required"
        
    try:
        amount = float(claim_amount)
        if amount <= 0:
            return False, "Claim amount must be greater than zero"
    except ValueError:
        return False, "Claim amount must be a valid number"

    if not policy_id:
        return False, "Policy ID is required"

    if not claim_date:
        return False, "Claim date is required"
        
    try:
        datetime.strptime(claim_date, "%Y-%m-%d")
    except ValueError:
        return False, "Claim date must be in YYYY-MM-DD format"

    return True, ""
