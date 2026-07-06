"""
===========================================================
Healthcare Fraud Detection System
Configuration File
===========================================================

Author : Team 5

This file stores all application settings.

If you need to change:
1. Database
2. Secret Key
3. ML Model Path
4. Upload Folder

Edit the .env file instead of this file whenever possible.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    # ======================================================
    # Flask Configuration
    # ======================================================

    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "healthcare_fraud_secret_key"
    )

    DEBUG = os.getenv(
        "DEBUG",
        "True"
    ) == "True"

    # ======================================================
    # Database Configuration
    # ======================================================

    # SQLite Database
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "database", "claims.db"))
    
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{DB_PATH}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ======================================================
    # JWT Configuration
    # ======================================================

    JWT_SECRET_KEY = os.getenv(
        "JWT_SECRET_KEY",
        "healthcare_fraud_jwt_secret"
    )

    JWT_ACCESS_TOKEN_EXPIRES = 3600

    # ======================================================
    # Upload Folder
    # ======================================================

    UPLOAD_FOLDER = os.getenv(
        "UPLOAD_FOLDER",
        "uploads"
    )

    # ======================================================
    # ML Model Paths
    # ======================================================

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    MODEL_PATH = os.path.join(
        BASE_DIR,
        "..",
        "ml",
        "models",
        "fraud_model.pkl"
    )

    ENCODER_PATH = os.path.join(
        BASE_DIR,
        "..",
        "ml",
        "models",
        "encoder.pkl"
    )

    SCALER_PATH = os.path.join(
        BASE_DIR,
        "..",
        "ml",
        "models",
        "scaler.pkl"
    )

    FEATURE_COLUMNS_PATH = os.path.join(
        BASE_DIR,
        "..",
        "ml",
        "models",
        "feature_columns.pkl"
    )

    # ======================================================
    # Project Information
    # ======================================================

    PROJECT_NAME = "Healthcare Fraud Detection System"

    VERSION = "1.0.0"

    API_PREFIX = "/api"

    # ======================================================
    # Allowed File Extensions
    # ======================================================

    ALLOWED_EXTENSIONS = {
        "csv",
        "xlsx",
        "xls"
    }