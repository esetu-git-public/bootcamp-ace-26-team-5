from functools import wraps
from flask_jwt_extended import get_jwt, verify_jwt_in_request
from utils.response import error_response

def role_required(*allowed_roles):
    """
    Decorator to restrict access to endpoints based on user roles.
    Allowed roles are defined as parameters (e.g., @role_required('admin', 'investigator')).
    Requires valid JWT token.
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Ensure JWT is verified for this request first
            verify_jwt_in_request()
            
            # Extract claims
            claims = get_jwt()
            user_role = claims.get("role")
            
            if not user_role or user_role not in allowed_roles:
                return error_response(
                    message=f"Access forbidden: requires one of roles: {', '.join(allowed_roles)}",
                    status_code=403
                )
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator
