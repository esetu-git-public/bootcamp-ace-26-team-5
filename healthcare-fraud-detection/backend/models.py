from datetime import datetime, date

class User:
    def __init__(self, user_id=None, full_name="", email="", password_hash="", role="employee", created_at=None):
        self.user_id = user_id
        self.full_name = full_name
        self.email = email
        self.password_hash = password_hash
        self.role = role
        self.created_at = created_at or datetime.utcnow()

    @staticmethod
    def from_dict(data):
        if not data:
            return None
        return User(
            user_id=data.get("user_id"),
            full_name=data.get("full_name"),
            email=data.get("email"),
            password_hash=data.get("password_hash"),
            role=data.get("role", "employee"),
            created_at=data.get("created_at")
        )

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "full_name": self.full_name,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }


class Policyholder:
    def __init__(self, policyholder_id=None, full_name="", date_of_birth=None, gender=None, phone=None, email=None, address=None, city=None, state=None, created_at=None):
        self.policyholder_id = policyholder_id
        self.full_name = full_name
        self.date_of_birth = date_of_birth
        self.gender = gender
        self.phone = phone
        self.email = email
        self.address = address
        self.city = city
        self.state = state
        self.created_at = created_at or datetime.utcnow()

    @staticmethod
    def from_dict(data):
        if not data:
            return None
        return Policyholder(
            policyholder_id=data.get("policyholder_id"),
            full_name=data.get("full_name"),
            date_of_birth=data.get("date_of_birth"),
            gender=data.get("gender"),
            phone=data.get("phone"),
            email=data.get("email"),
            address=data.get("address"),
            city=data.get("city"),
            state=data.get("state"),
            created_at=data.get("created_at")
        )

    def to_dict(self):
        dob_str = self.date_of_birth
        if isinstance(self.date_of_birth, (date, datetime)):
            dob_str = self.date_of_birth.isoformat()
        return {
            "policyholder_id": self.policyholder_id,
            "full_name": self.full_name,
            "date_of_birth": dob_str,
            "gender": self.gender,
            "phone": self.phone,
            "email": self.email,
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }


class InsurancePolicy:
    def __init__(self, policy_id=None, policy_number="", policyholder_id=None, insurance_type="", start_date=None, end_date=None, premium_amount=None, coverage_amount=None, policy_status="active"):
        self.policy_id = policy_id
        self.policy_number = policy_number
        self.policyholder_id = policyholder_id
        self.insurance_type = insurance_type
        self.start_date = start_date
        self.end_date = end_date
        self.premium_amount = premium_amount
        self.coverage_amount = coverage_amount
        self.policy_status = policy_status

    @staticmethod
    def from_dict(data):
        if not data:
            return None
        return InsurancePolicy(
            policy_id=data.get("policy_id"),
            policy_number=data.get("policy_number"),
            policyholder_id=data.get("policyholder_id"),
            insurance_type=data.get("insurance_type"),
            start_date=data.get("start_date"),
            end_date=data.get("end_date"),
            premium_amount=data.get("premium_amount"),
            coverage_amount=data.get("coverage_amount"),
            policy_status=data.get("policy_status", "active")
        )

    def to_dict(self):
        start_str = self.start_date
        if isinstance(self.start_date, (date, datetime)):
            start_str = self.start_date.isoformat()
        end_str = self.end_date
        if isinstance(self.end_date, (date, datetime)):
            end_str = self.end_date.isoformat()
        return {
            "policy_id": self.policy_id,
            "policy_number": self.policy_number,
            "policyholder_id": self.policyholder_id,
            "insurance_type": self.insurance_type,
            "start_date": start_str,
            "end_date": end_str,
            "premium_amount": self.premium_amount,
            "coverage_amount": self.coverage_amount,
            "policy_status": self.policy_status
        }


class InsuranceClaim:
    def __init__(self, claim_id=None, claim_number="", policy_id=None, claim_date=None, incident_date=None, claim_type=None, claim_amount=None, incident_location=None, incident_description=None, police_report_available=0, witnesses_count=0, claim_status="submitted", submitted_by=None, created_at=None, prediction=None):
        self.claim_id = claim_id
        self.claim_number = claim_number
        self.policy_id = policy_id
        self.claim_date = claim_date
        self.incident_date = incident_date
        self.claim_type = claim_type
        self.claim_amount = claim_amount
        self.incident_location = incident_location
        self.incident_description = incident_description
        self.police_report_available = police_report_available
        self.witnesses_count = witnesses_count
        self.claim_status = claim_status
        self.submitted_by = submitted_by
        self.created_at = created_at or datetime.utcnow()
        self.prediction = prediction  # FraudPrediction object or dict

    @staticmethod
    def from_dict(data):
        if not data:
            return None
        # Handle nested prediction if available
        pred = data.get("prediction")
        if pred and isinstance(pred, dict):
            pred = FraudPrediction.from_dict(pred)
        return InsuranceClaim(
            claim_id=data.get("claim_id"),
            claim_number=data.get("claim_number"),
            policy_id=data.get("policy_id"),
            claim_date=data.get("claim_date"),
            incident_date=data.get("incident_date"),
            claim_type=data.get("claim_type"),
            claim_amount=data.get("claim_amount"),
            incident_location=data.get("incident_location"),
            incident_description=data.get("incident_description"),
            police_report_available=data.get("police_report_available", 0),
            witnesses_count=data.get("witnesses_count", 0),
            claim_status=data.get("claim_status", "submitted"),
            submitted_by=data.get("submitted_by"),
            created_at=data.get("created_at"),
            prediction=pred
        )

    def to_dict(self):
        c_date = self.claim_date
        if isinstance(self.claim_date, (date, datetime)):
            c_date = self.claim_date.isoformat()
        i_date = self.incident_date
        if isinstance(self.incident_date, (date, datetime)):
            i_date = self.incident_date.isoformat()
        return {
            "claim_id": self.claim_id,
            "claim_number": self.claim_number,
            "policy_id": self.policy_id,
            "claim_date": c_date,
            "incident_date": i_date,
            "claim_type": self.claim_type,
            "claim_amount": self.claim_amount,
            "incident_location": self.incident_location,
            "incident_description": self.incident_description,
            "police_report_available": bool(self.police_report_available),
            "witnesses_count": self.witnesses_count,
            "claim_status": self.claim_status,
            "submitted_by": self.submitted_by,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "policy": getattr(self, "policy_embedded", None)
        }


class FraudPrediction:
    def __init__(self, prediction_id=None, claim_id=None, predicted_label="", fraud_probability=0.0, risk_level=None, model_version="v1.0", prediction_date=None, remarks=None):
        self.prediction_id = prediction_id
        self.claim_id = claim_id
        self.predicted_label = predicted_label
        self.fraud_probability = fraud_probability
        self.risk_level = risk_level
        self.model_version = model_version
        self.prediction_date = prediction_date or datetime.utcnow()
        self.remarks = remarks

    @staticmethod
    def from_dict(data):
        if not data:
            return None
        return FraudPrediction(
            prediction_id=data.get("prediction_id"),
            claim_id=data.get("claim_id"),
            predicted_label=data.get("predicted_label"),
            fraud_probability=data.get("fraud_probability", 0.0),
            risk_level=data.get("risk_level"),
            model_version=data.get("model_version", "v1.0"),
            prediction_date=data.get("prediction_date"),
            remarks=data.get("remarks")
        )

    def to_dict(self):
        p_date = self.prediction_date
        if isinstance(self.prediction_date, (date, datetime)):
            p_date = self.prediction_date.isoformat()
        remarks_list = [r.strip() for r in (self.remarks or "").split(",") if r.strip()]
        return {
            "prediction_id": self.prediction_id,
            "claim_id": self.claim_id,
            "predicted_label": self.predicted_label,
            "predictedLabel": self.predicted_label,
            "fraud_probability": self.fraud_probability,
            "probability": self.fraud_probability,
            "risk_level": self.risk_level,
            "riskLevel": self.risk_level,
            "model_version": self.model_version,
            "modelVersion": self.model_version,
            "prediction_date": p_date,
            "remarks": self.remarks,
            "explanations": remarks_list
        }


class AuditLog:
    def __init__(self, log_id=None, user_id=None, claim_id=None, action="", details=None, timestamp=None):
        self.log_id = log_id
        self.user_id = user_id
        self.claim_id = claim_id
        self.action = action
        self.details = details
        self.timestamp = timestamp or datetime.utcnow()

    @staticmethod
    def from_dict(data):
        if not data:
            return None
        return AuditLog(
            log_id=data.get("log_id"),
            user_id=data.get("user_id"),
            claim_id=data.get("claim_id"),
            action=data.get("action"),
            details=data.get("details"),
            timestamp=data.get("timestamp")
        )

    def to_dict(self):
        return {
            "log_id": self.log_id,
            "user_id": self.user_id,
            "claim_id": self.claim_id,
            "action": self.action,
            "details": self.details,
            "timestamp": self.timestamp.isoformat() if isinstance(self.timestamp, datetime) else self.timestamp
        }
