"""
==========================================================
Healthcare Fraud Detection System
Database Configuration
==========================================================

Author : Team 5

Purpose:
---------
1. Connect Flask with SQLite Database
2. Initialize SQLAlchemy
3. Create Database Tables

Database Used:
--------------
SQLite

Database File:
--------------
database/claims.db
"""

from flask_sqlalchemy import SQLAlchemy

# SQLAlchemy Object
db = SQLAlchemy()


def initialize_database(app):
    """
    Initialize database with Flask app.
    """

    db.init_app(app)

    with app.app_context():

        db.create_all()

        print("=" * 50)
        print("Database Connected Successfully")
        print("Tables Created Successfully")
        print("=" * 50)