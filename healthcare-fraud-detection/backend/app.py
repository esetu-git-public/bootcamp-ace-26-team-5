"""
=====================================================
Healthcare Fraud Detection System
Backend Entry Point (Flask)
=====================================================

Author: Team 5

This file is responsible for:

1. Creating Flask App
2. Loading Configurations
3. Connecting Database
4. Registering Routes
5. Starting Server

"""

from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os

# -----------------------------
# Load Environment Variables
# -----------------------------
load_dotenv()

# -----------------------------
# Import Local Files
# -----------------------------
from database import db, initialize_database
try:
    from config import Config
except ImportError:
    from .config import Config

# These files will be created later
from auth import auth_bp
from routes import claim_bp

# -----------------------------
# Create Flask App
# -----------------------------
app = Flask(__name__)

# Load Configurations
app.config.from_object(Config)

# Enable CORS
CORS(app)

# Initialize Database
initialize_database(app)

# ---------------------------------------
# Register Blueprints
# ---------------------------------------

app.register_blueprint(auth_bp, url_prefix="/api/auth")

app.register_blueprint(claim_bp, url_prefix="/api/claims")


# ---------------------------------------
# Health Check
# ---------------------------------------

@app.route("/", methods=["GET"])
def home():

    return jsonify({

        "project": "Healthcare Fraud Detection System",

        "version": "1.0",

        "status": "Running",

        "message": "Backend Server Running Successfully"

    })


@app.route("/health", methods=["GET"])
def health():

    return jsonify({

        "status": "Healthy",

        "database": "Connected",

        "ml_model": "Ready"

    })


# ---------------------------------------
# Error Handlers
# ---------------------------------------

@app.errorhandler(404)
def page_not_found(error):

    return jsonify({

        "success": False,

        "message": "API Endpoint Not Found"

    }),404


@app.errorhandler(500)
def internal_error(error):

    return jsonify({

        "success": False,

        "message": "Internal Server Error"

    }),500





# ---------------------------------------
# Run Application
# ---------------------------------------

if __name__ == "__main__":

    app.run(

        host="0.0.0.0",

        port=5000,

        debug=True

    )
