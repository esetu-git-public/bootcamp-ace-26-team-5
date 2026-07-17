from datetime import datetime

from datetime import datetime

def validate_claim_payload(data: dict) -> tuple[bool, str]:
    """
    Validate claims input data. Supports standard database format, old frontend format,
    and the new minified optimized frontend format.
    Returns (is_valid, error_message).
    """
    if not data:
        return False, "Request payload is empty"

    # 1. Check if it's the new optimized frontend format or old frontend format
    is_frontend = "claimAmount" in data or "patientName" in data or "serviceDate" in data
    
    if is_frontend:
        claim_amount = data.get("claimAmount")
        if claim_amount is None:
            return False, "Claim amount is required"
            
        try:
            amount = float(claim_amount)
            if amount <= 0:
                return False, "Claim amount must be greater than zero"
        except ValueError:
            return False, "Claim amount must be a valid number"

        # Check for serviceDate (required in new optimized format)
        service_date = data.get("serviceDate")
        if service_date:
            try:
                datetime.strptime(str(service_date), "%Y-%m-%d")
            except ValueError:
                return False, "Service date must be in YYYY-MM-DD format"
        elif "patientName" not in data:
            # If not old format, serviceDate is required
            return False, "Service date is required"

        # Check provider/hospital
        provider = data.get("provider") or data.get("hospital")
        if not provider and "patientName" not in data:
            return False, "Provider / Hospital name is required"

        # Check diagnosis
        diagnosis = data.get("diagnosis")
        if not diagnosis and "patientName" not in data:
            return False, "Diagnosis is required"

        # Check procedure
        procedure = data.get("procedure")
        if not procedure and "patientName" not in data:
            return False, "Procedure code is required"

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
