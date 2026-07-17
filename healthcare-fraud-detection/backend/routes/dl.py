"""
===========================================================
Healthcare Fraud Detection System
Deep Learning Engine Routes (Controller)
===========================================================

This module registers blueprint routes for querying deep learning model health.
"""

import sys
from pathlib import Path
import os
from flask import Blueprint
from flask_jwt_extended import jwt_required
from utils.api_response import success_response, error_response

# Resolve paths to dl/inference/v1
BASE_DIR = Path(__file__).resolve().parent.parent
DL_INFERENCE_DIR = os.path.abspath(BASE_DIR / ".." / "dl" / "inference" / "v1")
if DL_INFERENCE_DIR not in sys.path:
    sys.path.append(DL_INFERENCE_DIR)

from predict import get_model_health_status

dl_bp = Blueprint("dl", __name__)

@dl_bp.route("/health", methods=["GET"])
@jwt_required(optional=True)
def get_dl_health():
    """
    GET /api/dl/health
    Returns loaded model details, active engine backend, and performance metadata.
    """
    try:
        health_data = get_model_health_status()
        return success_response(
            data=health_data,
            message="Deep Learning engine health check successful"
        )
    except Exception as e:
        return error_response(
            message=f"Deep Learning engine is unhealthy: {str(e)}",
            status_code=500
        )
