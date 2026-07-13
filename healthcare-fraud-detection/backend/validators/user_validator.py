"""
===========================================================
Healthcare Fraud Detection System
User Payload Validator
===========================================================

This module validates JSON input payloads for user registration and login.
"""

from typing import Tuple, Dict, Any
import re
from constants import ALLOWED_ROLES

EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")

def validate_registration_payload(data: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validate signup credentials and data structures.
    
    Args:
        data (dict): Request body payload.
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not data:
        return False, "Request payload is empty"
        
    full_name = data.get("full_name")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role", "employee")

    if not full_name or not full_name.strip():
        return False, "Full name is required"

    if not email or not email.strip():
        return False, "Email address is required"
        
    if not EMAIL_REGEX.match(email.strip()):
        return False, "Invalid email address format"

    if not password or len(password) < 6:
        return False, "Password must be at least 6 characters long"

    if role.strip().lower() not in ALLOWED_ROLES:
        return False, f"Invalid role. Allowed roles are: {', '.join(ALLOWED_ROLES)}"

    return True, ""


def validate_login_payload(data: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validate sign-in credentials structures.
    
    Args:
        data (dict): Request body payload.
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not data:
        return False, "Request payload is empty"

    email = data.get("email")
    password = data.get("password")

    if not email or not email.strip():
        return False, "Email address is required"

    if not password:
        return False, "Password is required"

    return True, ""
