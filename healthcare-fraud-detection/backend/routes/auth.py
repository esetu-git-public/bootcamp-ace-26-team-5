from flask import Blueprint, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt,
    verify_jwt_in_request
)
from datetime import timedelta

from repositories.user_repository import (
    find_user_by_email,
    create_user,
    find_user_by_id
)
from validators.auth_validator import (
    validate_registration_data,
    validate_login_data
)
from utils.security import hash_password, check_password
from utils.response import success_response, error_response
from services.audit_service import log_event

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    """
    User registration route. Enforces default customer role and generates JWT tokens.
    """
    data = request.get_json(silent=True)
    is_valid, err_msg = validate_registration_data(data)
    if not is_valid:
        return error_response(message=err_msg, status_code=400)

    email = data.get("email").strip().lower()
    
    # Enforce default role to customer on public registration
    # If a role other than 'customer' is requested, require a valid Admin token
    role = data.get("role", "customer").strip().lower()
    if role != "customer":
        try:
            verify_jwt_in_request(optional=True)
            claims = get_jwt()
            caller_role = claims.get("role") if claims else None
            if caller_role != "admin":
                role = "customer"
        except Exception:
            role = "customer"

    # Check if user already exists
    if find_user_by_email(email):
        return error_response(message=message_override if 'message_override' in locals() else "A user with this email address already exists", status_code=409)

    # Hash the password and save
    hashed = hash_password(data.get("password"))
    user = create_user(
        full_name=data.get("full_name") or data.get("name"),
        email=email,
        password_hash=hashed,
        role=role
    )
    
    if not user:
        return error_response(
            message="Database registration failed. The check constraint 'users_role_check' on the users table in Supabase may be rejecting the 'customer' role. Please execute database/patches/fix_users_role_check.sql in your Supabase SQL editor to resolve this.",
            status_code=400
        )

    # Generate JWT tokens for auto-login after signup
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
        action="USER_REGISTRATION",
        user_id=user.user_id,
        details=f"User {email} registered successfully with role {role}."
    )

    return success_response(
        data={
            "access_token": access_token,
            "accessToken": access_token,
            "refresh_token": refresh_token,
            "refreshToken": refresh_token,
            "user": user.to_dict()
        },
        message="User registered successfully",
        status_code=201
    )


@auth_bp.route("/signup", methods=["POST"])
def signup():
    """
    Alias route for /signup to map frontend routes.
    """
    return register()


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    User login route. Generates JWT access and refresh tokens.
    """
    data = request.get_json(silent=True)
    is_valid, err_msg = validate_login_data(data)
    if not is_valid:
        return error_response(message=err_msg, status_code=400)

    email = data.get("email").strip().lower()
    password = data.get("password")

    user = find_user_by_email(email)
    if not user or not check_password(password, user.password_hash):
        return error_response(message="Invalid email or password", status_code=401)

    # Create tokens (Access expires in 1 hour, Refresh expires in 7 days)
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

    return success_response(
        data={
            "access_token": access_token,
            "accessToken": access_token,
            "refresh_token": refresh_token,
            "refreshToken": refresh_token,
            "user": user.to_dict()
        },
        message="Login successful",
        status_code=200
    )


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    """
    Refresh JWT access tokens using a valid refresh token.
    """
    current_user_id = get_jwt_identity()
    user = find_user_by_id(int(current_user_id))
    
    if not user:
        return error_response("User not found", 401)

    additional_claims = {"role": user.role, "full_name": user.full_name}
    new_access_token = create_access_token(
        identity=str(user.user_id),
        additional_claims=additional_claims,
        expires_delta=timedelta(hours=1)
    )

    return success_response(
        data={
            "access_token": new_access_token,
            "accessToken": new_access_token
        },
        message="Token refreshed successfully"
    )


@auth_bp.route("/logout", methods=["POST"])
def logout():
    """
    Logout route. Handles validation errors gracefully for expired tokens.
    """
    try:
        verify_jwt_in_request(optional=True)
        user_id = get_jwt_identity()
        if user_id:
            log_event(
                action="USER_LOGOUT",
                user_id=int(user_id),
                details="User logged out successfully."
            )
    except Exception:
        pass
    return success_response(message="Logged out successfully")


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    """
    Retrieve profile details of the currently authenticated user.
    """
    user_id = get_jwt_identity()
    user = find_user_by_id(int(user_id))
    if not user:
        return error_response("User profile not found", 404)
        
    return success_response(data=user.to_dict())
