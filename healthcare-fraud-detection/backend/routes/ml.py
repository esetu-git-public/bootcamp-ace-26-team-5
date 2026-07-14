"""
===========================================================
Healthcare Fraud Detection System
Machine Learning Engine Routes (Controller)
===========================================================

This module registers blueprint routes for querying machine learning model health.
"""

import sys
from pathlib import Path
import os
from flask import Blueprint
from flask_jwt_extended import jwt_required
from utils.api_response import success_response, error_response

# Resolve paths to ml/inference/v1
BASE_DIR = Path(__file__).resolve().parent.parent
ML_INFERENCE_DIR = os.path.abspath(BASE_DIR / ".." / "ml" / "inference" / "v1")
if ML_INFERENCE_DIR not in sys.path:
    sys.path.append(ML_INFERENCE_DIR)

from predict import get_model_health_status

ml_bp = Blueprint("ml", __name__)

@ml_bp.route("/health", methods=["GET"])
@jwt_required(optional=True)
def get_ml_health():
    """
    GET /api/ml/health
    Returns loaded model details, active engine backend (Keras 3 vs RF fallback),
    and performance metadata.
    """
    try:
        health_data = get_model_health_status()
        return success_response(
            data=health_data,
            message="Machine Learning engine health check successful"
        )
    except Exception as e:
        return error_response(
            message=f"Machine Learning engine is unhealthy: {str(e)}",
            status_code=500
        )
