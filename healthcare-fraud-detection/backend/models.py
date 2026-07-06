from datetime import datetime
from database import db

class User(db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default="employee")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    claims = db.relationship("InsuranceClaim", backref="submitter", lazy=True)
    audit_logs = db.relationship("AuditLog", backref="user", lazy=True)

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "full_name": self.full_name,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class Policyholder(db.Model):
    __tablename__ = "policyholders"

    policyholder_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    full_name = db.Column(db.String(100), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(20), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(100), unique=True, nullable=True)
    address = db.Column(db.Text, nullable=True)
    city = db.Column(db.String(50), nullable=True)
    state = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    policies = db.relationship("InsurancePolicy", backref="holder", lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "policyholder_id": self.policyholder_id,
            "full_name": self.full_name,
            "date_of_birth": self.date_of_birth.isoformat() if self.date_of_birth else None,
            "gender": self.gender,
            "phone": self.phone,
            "email": self.email,
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class InsurancePolicy(db.Model):
    __tablename__ = "insurance_policies"

    policy_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    policy_number = db.Column(db.String(50), unique=True, nullable=False)
    policyholder_id = db.Column(db.Integer, db.ForeignKey("policyholders.policyholder_id", ondelete="CASCADE"), nullable=False)
    insurance_type = db.Column(db.String(50), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    premium_amount = db.Column(db.Float, nullable=True)
    coverage_amount = db.Column(db.Float, nullable=True)
    policy_status = db.Column(db.String(50), default="active")

    # Relationships
    claims = db.relationship("InsuranceClaim", backref="policy", lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "policy_id": self.policy_id,
            "policy_number": self.policy_number,
            "policyholder_id": self.policyholder_id,
            "insurance_type": self.insurance_type,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "premium_amount": self.premium_amount,
            "coverage_amount": self.coverage_amount,
            "policy_status": self.policy_status
        }


class InsuranceClaim(db.Model):
    __tablename__ = "insurance_claims"

    claim_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    claim_number = db.Column(db.String(50), unique=True, nullable=False)
    policy_id = db.Column(db.Integer, db.ForeignKey("insurance_policies.policy_id", ondelete="CASCADE"), nullable=False)
    claim_date = db.Column(db.Date, nullable=False)
    incident_date = db.Column(db.Date, nullable=True)
    claim_type = db.Column(db.String(50), nullable=True)
    claim_amount = db.Column(db.Float, nullable=False)
    incident_location = db.Column(db.String(100), nullable=True)
    incident_description = db.Column(db.Text, nullable=True)
    police_report_available = db.Column(db.Integer, default=0)
    witnesses_count = db.Column(db.Integer, default=0)
    claim_status = db.Column(db.String(50), default="submitted")
    submitted_by = db.Column(db.Integer, db.ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    prediction = db.relationship("FraudPrediction", backref="claim", uselist=False, cascade="all, delete-orphan")
    audit_logs = db.relationship("AuditLog", backref="claim", lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "claim_id": self.claim_id,
            "claim_number": self.claim_number,
            "policy_id": self.policy_id,
            "claim_date": self.claim_date.isoformat() if self.claim_date else None,
            "incident_date": self.incident_date.isoformat() if self.incident_date else None,
            "claim_type": self.claim_type,
            "claim_amount": self.claim_amount,
            "incident_location": self.incident_location,
            "incident_description": self.incident_description,
            "police_report_available": bool(self.police_report_available),
            "witnesses_count": self.witnesses_count,
            "claim_status": self.claim_status,
            "submitted_by": self.submitted_by,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class FraudPrediction(db.Model):
    __tablename__ = "fraud_predictions"

    prediction_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    claim_id = db.Column(db.Integer, db.ForeignKey("insurance_claims.claim_id", ondelete="CASCADE"), nullable=False)
    predicted_label = db.Column(db.String(20), nullable=False)  # 'Fraud' or 'Not Fraud'
    fraud_probability = db.Column(db.Float, nullable=False)
    risk_level = db.Column(db.String(20), nullable=True)  # 'Low', 'Medium', 'High'
    model_version = db.Column(db.String(50), nullable=True, default="v1.0")
    prediction_date = db.Column(db.DateTime, default=datetime.utcnow)
    remarks = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            "prediction_id": self.prediction_id,
            "claim_id": self.claim_id,
            "predicted_label": self.predicted_label,
            "fraud_probability": self.fraud_probability,
            "risk_level": self.risk_level,
            "model_version": self.model_version,
            "prediction_date": self.prediction_date.isoformat() if self.prediction_date else None,
            "remarks": self.remarks
        }


class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    log_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)
    claim_id = db.Column(db.Integer, db.ForeignKey("insurance_claims.claim_id", ondelete="CASCADE"), nullable=True)
    action = db.Column(db.String(100), nullable=False)  # e.g., 'LOGIN', 'CLAIM_CREATION', 'STATUS_CHANGE'
    details = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "log_id": self.log_id,
            "user_id": self.user_id,
            "claim_id": self.claim_id,
            "action": self.action,
            "details": self.details,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }
