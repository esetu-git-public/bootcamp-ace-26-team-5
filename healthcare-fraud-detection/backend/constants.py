"""
===========================================================
Healthcare Fraud Detection System
System Constants
===========================================================

This module contains system-wide constants for roles, claim statuses,
and risk levels to prevent magic strings and improve code quality.
"""

# User Roles
ROLE_ADMIN = "admin"
ROLE_EMPLOYEE = "employee"
ROLE_INVESTIGATOR = "investigator"
ROLE_SUPERVISOR = "supervisor"
ROLE_CUSTOMER = "customer"

ALLOWED_ROLES = {ROLE_ADMIN, ROLE_EMPLOYEE, ROLE_INVESTIGATOR, ROLE_SUPERVISOR, ROLE_CUSTOMER}

# Claim Statuses
STATUS_SUBMITTED = "submitted"
STATUS_UNDER_REVIEW = "under_review"
STATUS_APPROVED = "approved"
STATUS_REJECTED = "rejected"

ALLOWED_STATUSES = {STATUS_SUBMITTED, STATUS_UNDER_REVIEW, STATUS_APPROVED, STATUS_REJECTED}

# Risk Levels
RISK_LOW = "Low"
RISK_MEDIUM = "Medium"
RISK_HIGH = "High"

ALLOWED_RISK_LEVELS = {RISK_LOW, RISK_MEDIUM, RISK_HIGH}

# Prediction Labels
LABEL_FRAUD = "Fraud"
LABEL_NOT_FRAUD = "Not Fraud"

ALLOWED_LABELS = {LABEL_FRAUD, LABEL_NOT_FRAUD}
