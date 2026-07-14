"""
===========================================================
Healthcare Fraud Detection System
Standardized API Response Layer
===========================================================

This module provides helper functions to standardize all JSON responses returned by
the Flask endpoints, including request IDs and timestamps.
"""

from flask import jsonify, g
from datetime import datetime

def api_response(success: bool, message: str, data: dict = None, status_code: int = 200):
    """
    Generate a standardized API response dictionary.
    
    Args:
        success (bool): True if operation was successful, False otherwise.
        message (str): A user-friendly message describing the outcome.
        data (dict, optional): Payload data. Defaults to empty dictionary.
        status_code (int): HTTP status code. Defaults to 200.
        
    Returns:
        tuple: (flask.Response, int) status tuple.
    """
    # Extract request_id from Flask global g if available
    try:
        request_id = getattr(g, "request_id", "-")
    except RuntimeError:
        request_id = "-"

    payload = {
        "success": success,
        "message": message,
        "data": data if data is not None else {},
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "request_id": request_id
    }
    
    return jsonify(payload), status_code


def success_response(message: str = "Success", data: dict = None, status_code: int = 200):
    """
    Return a standardized successful API response.
    """
    return api_response(success=True, message=message, data=data, status_code=status_code)


def error_response(message: str = "An error occurred", status_code: int = 400, errors: dict = None):
    """
    Return a standardized error API response.
    """
    payload = {"errors": errors} if errors is not None else {}
    return api_response(success=False, message=message, data=payload, status_code=status_code)
