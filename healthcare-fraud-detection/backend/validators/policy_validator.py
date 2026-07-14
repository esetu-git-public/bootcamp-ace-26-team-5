"""
===========================================================
Healthcare Fraud Detection System
Policy Payload Validator
===========================================================

This module validates JSON input data for insurance policy creation and modification.
"""

from typing import Tuple, Dict, Any
from datetime import datetime

def validate_policy_payload(data: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validate policy parameter payloads.
    
    Args:
        data (dict): Request body parameters.
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not data:
        return False, "Request payload is empty"
        
    policy_number = data.get("policy_number")
    insurance_type = data.get("insurance_type")
    start_date_str = data.get("start_date")
    end_date_str = data.get("end_date")
    premium_amount = data.get("premium_amount")
    coverage_amount = data.get("coverage_amount")

    if not policy_number or not policy_number.strip():
        return False, "Policy number is required"
        
    if not insurance_type or not insurance_type.strip():
        return False, "Insurance type is required"

    if not start_date_str:
        return False, "Start date is required"
    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    except ValueError:
        return False, "Start date must be in YYYY-MM-DD format"

    if not end_date_str:
        return False, "End date is required"
    try:
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        if end_date < start_date:
            return False, "End date cannot be before start date"
    except ValueError:
        return False, "End date must be in YYYY-MM-DD format"

    if premium_amount is not None:
        try:
            p_amt = float(premium_amount)
            if p_amt < 0:
                return False, "Premium amount cannot be negative"
        except ValueError:
            return False, "Premium amount must be a valid number"

    if coverage_amount is not None:
        try:
            c_amt = float(coverage_amount)
            if c_amt < 0:
                return False, "Coverage amount cannot be negative"
        except ValueError:
            return False, "Coverage amount must be a valid number"

    return True, ""
