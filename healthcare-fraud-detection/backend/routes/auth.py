from flask import Blueprint, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
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
    User registration route.
    """
    data = request.get_json(silent=True)
    is_valid, err_msg = validate_registration_data(data)
    if not is_valid:
        return error_response(message=err_msg, status_code=400)

    email = data.get("email").strip().lower()
    role = data.get("role", "employee").strip().lower()

    # Check if user already exists
    if find_user_by_email(email):
        return error_response(message="A user with this email address already exists", status_code=409)

    # Hash the password and save
    hashed = hash_password(data.get("password"))
    user = create_user(
        full_name=data.get("full_name"),
        email=email,
        password_hash=hashed,
        role=role
    )

    # Log audit event
    log_event(
        action="USER_REGISTRATION",
        user_id=user.user_id,
        details=f"User {email} registered successfully with role {role}."
    )

    return success_response(
        data=user.to_dict(),
        message="User registered successfully",
        status_code=201
    )


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
            "refresh_token": refresh_token,
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
        data={"access_token": new_access_token},
        message="Token refreshed successfully"
    )


@auth_bp.route("/logout", methods=["POST"])
@jwt_required(optional=True)
def logout():
    """
    Logout route. Triggers audit event if user is authenticated.
    """
    user_id = get_jwt_identity()
    if user_id:
        log_event(
            action="USER_LOGOUT",
            user_id=int(user_id),
            details="User logged out successfully."
        )
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
