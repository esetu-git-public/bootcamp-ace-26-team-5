from flask import Blueprint
from werkzeug.exceptions import HTTPException
from utils.response import error_response
from utils.logger import logger

error_bp = Blueprint("errors", __name__)

@error_bp.app_errorhandler(Exception)
def handle_global_exception(e):
    """
    Catch-all error handler for any uncaught exceptions.
    """
    # If the exception is a standard Flask HTTP exception, preserve its code
    if isinstance(e, HTTPException):
        logger.warning(f"HTTPException {e.code}: {e.description}")
        return error_response(
            message=e.description,
            status_code=e.code
        )
    
    # Log the full traceback internally
    logger.exception(f"Unhandled system error: {str(e)}")
    
    # Return a secure, generic error message to the client
    return error_response(
        message="An internal server error occurred.",
        status_code=500
    )


@error_bp.app_errorhandler(404)
def handle_not_found(e):
    return error_response("Resource not found.", 404)


@error_bp.app_errorhandler(405)
def handle_method_not_allowed(e):
    return error_response("Method not allowed for this route.", 405)


@error_bp.app_errorhandler(400)
def handle_bad_request(e):
    return error_response(str(e.description) if hasattr(e, 'description') else "Bad request.", 400)
