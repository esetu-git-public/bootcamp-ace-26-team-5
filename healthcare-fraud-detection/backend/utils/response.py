from flask import jsonify

def success_response(data=None, message="Success", status_code=200):
    """
    Generate a standardized successful JSON response.
    """
    response = {
        "success": True,
        "message": message
    }
    if data is not None:
        response["data"] = data
    return jsonify(response), status_code


def error_response(message="An error occurred", status_code=400, errors=None):
    """
    Generate a standardized error JSON response.
    """
    response = {
        "success": False,
        "message": message
    }
    if errors is not None:
        response["errors"] = errors
    return jsonify(response), status_code
