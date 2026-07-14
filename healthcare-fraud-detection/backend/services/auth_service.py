"""
===========================================================
Healthcare Fraud Detection System
Authentication Service
===========================================================

This module implements core authentication services, including user login,
registration with role validation, and JWT token issuance.
"""

from typing import Tuple, Dict, Any, Optional
from datetime import timedelta
from flask_jwt_extended import create_access_token, create_refresh_token

from repositories.user_repository import (
    find_user_by_email,
    create_user,
    find_user_by_id
)
from utils.security import hash_password, check_password
from services.audit_service import log_event
from constants import ROLE_EMPLOYEE, ROLE_ADMIN
from utils.logger import logger

def register_user(data: Dict[str, Any], performing_user_role: Optional[str] = None) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Register a new system user, applying role restriction logic to prevent privilege escalation.
    
    Args:
        data (dict): Registration parameters (email, full_name, password, role).
        performing_user_role (str, optional): Role of active user requesting registration.
        
    Returns:
        tuple: (success, message, user_data_dict)
    """
    email = data.get("email").strip().lower()
    role = data.get("role", ROLE_EMPLOYEE).strip().lower()

    # Role Escalation Protection: Public signups default to employee.
    # Non-standard roles require active admin session authorization.
    if role != ROLE_EMPLOYEE and performing_user_role != ROLE_ADMIN:
        logger.warning(
            f"Unauthorized role assignment request for {email}: role={role}. "
            f"Overriding to default employee."
        )
        role = ROLE_EMPLOYEE

    # Verify if email already exists
    if find_user_by_email(email):
        return False, "A user with this email address already exists", {}

    # Hash password and create record
    hashed = hash_password(data.get("password"))
    user = create_user(
        full_name=data.get("full_name"),
        email=email,
        password_hash=hashed,
        role=role
    )
    
    if not user:
        return False, "Failed to create user account", {}

    # Log audit trail
    log_event(
        action="USER_REGISTRATION",
        user_id=user.user_id,
        details=f"User {email} registered successfully with role {role}."
    )

    return True, "User registered successfully", user.to_dict()


def login_user(data: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Authenticate user credentials, logging actions and issuing JWT access and refresh tokens.
    
    Args:
        data (dict): Login credentials (email, password).
        
    Returns:
        tuple: (success, message, token_payload_dict)
    """
    email = data.get("email").strip().lower()
    password = data.get("password")

    user = find_user_by_email(email)
    if not user or not check_password(password, user.password_hash):
        logger.warning(f"Failed login attempt for email: {email}")
        return False, "Invalid email or password", {}

    # Standard token claims (claims are serialized in the token body)
    additional_claims = {"role": user.role, "full_name": user.full_name}
    
    access_token = create_access_token(
        identity=str(user.user_id),
        additional_claims=additional_claims,
        expires_delta=timedelta(hours=1)
    )
    refresh_token = create_refresh_token(
        identity=str(user.user_id),
        expires_delta=timedelta(days=7)
    )

    # Log audit event
    log_event(
        action="USER_LOGIN",
        user_id=user.user_id,
        details=f"User {email} logged in successfully."
    )

    return True, "Login successful", {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": user.to_dict()
    }


def refresh_user_token(user_id: int) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Re-issue a valid access token using claims.
    """
    user = find_user_by_id(user_id)
    if not user:
        return False, "User not found", {}

    additional_claims = {"role": user.role, "full_name": user.full_name}
    new_access_token = create_access_token(
        identity=str(user.user_id),
        additional_claims=additional_claims,
        expires_delta=timedelta(hours=1)
    )
    
    return True, "Token refreshed successfully", {"access_token": new_access_token}


def get_user_profile(user_id: int) -> Optional[Dict[str, Any]]:
    """
    Retrieve user record mapped to JSON payload.
    """
    user = find_user_by_id(user_id)
    return user.to_dict() if user else None
