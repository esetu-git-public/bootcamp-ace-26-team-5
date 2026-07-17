from datetime import datetime, date, timedelta
import random

from models import InsuranceClaim, Policyholder, InsurancePolicy, FraudPrediction
from repositories.claim_repository import (
    find_claim_by_id,
    save_claim as db_save_claim,
    delete_claim as db_delete_claim
)
from repositories.policyholder_repository import (
    find_policyholder_by_name,
    find_policyholder_by_id,
    save_policyholder
)
from repositories.policy_repository import (
    find_policy_by_id,
    find_policy_by_policyholder_id,
    save_policy
)
from repositories.user_repository import find_users_by_role
from services.prediction_service import run_claim_prediction
from services.notification_service import send_notification
from services.audit_service import log_event
from utils.logger import logger

def create_claim_from_payload(data: dict, user_id: int = None) -> InsuranceClaim:
    """
    Business logic for creating a claim. Handles frontend form translation, 
    dynamic mock policy linkage, ML prediction scoring, auto-approval routing, 
    and audit logging.
    """
    logger.info("Processing claim creation payload...")
    
    # 1. Fetch user from user repository if user_id is provided
    from repositories.user_repository import find_user_by_id
    user = find_user_by_id(user_id) if user_id else None
    
    # Check if payload is in frontend form format or new minified format
    is_frontend_form = "claimAmount" in data or "patientName" in data
    
    if is_frontend_form:
        # Determine Patient Name
        if "patientName" in data:
            patient_name = data.get("patientName").strip()
            gender = data.get("gender", "Male").strip().capitalize()
            age = int(data.get("age", 45))
            diagnosis = data.get("diagnosis", "I10").strip()
            hospital = data.get("hospital", "General Hospital").strip()
            procedure = 99214 # fallback
            length_of_stay = int(data.get("lengthOfStay" if "lengthOfStay" in data else "length_of_stay", 0))
            service_date_str = data.get("dates", {}).get("serviceDate") or data.get("serviceDate")
        else:
            # Minified optimized format
            patient_name = user.full_name if user else "Ava Thompson"
            gender = "Female" # Default
            age = int(data.get("age", 45))
            diagnosis = data.get("diagnosis", "I10").strip()
            hospital = data.get("provider", "General Hospital").strip()
            procedure = int(data.get("procedure", 99214))
            length_of_stay = int(data.get("lengthOfStay", 0))
            service_date_str = data.get("serviceDate")
            
        claim_amount = float(data.get("claimAmount") or data.get("claim_amount", 150.0))
        
        # Resolve or create a Policyholder
        holder = find_policyholder_by_name(patient_name)
        if not holder:
            holder = Policyholder(
                full_name=patient_name,
                gender=gender,
                date_of_birth=date.today() - timedelta(days=age * 365.25),
                email=user.email if user else None,
                city="Hyderabad",
                state="Telangana"
            )
            holder = save_policyholder(holder)
            
        # Resolve or create a mock InsurancePolicy
        policy = find_policy_by_policyholder_id(holder.policyholder_id)
        if not policy:
            policy_num = f"POL-MOCK-{random.randint(1000, 9999)}"
            policy = InsurancePolicy(
                policy_number=policy_num,
                policyholder_id=holder.policyholder_id,
                insurance_type="Private",
                start_date=date.today() - timedelta(days=180),
                end_date=date.today() + timedelta(days=180),
                premium_amount=15000.0,
                coverage_amount=700000.0
            )
            policy = save_policy(policy)

        policy_id = policy.policy_id
        claim_type = "Medical"
        incident_desc = f"Treatment for diagnosis: {diagnosis} at {hospital}."
        incident_loc = holder.city or "Hyderabad"
        police_report = 0
        witnesses = 0
        claim_date_obj = date.today()
        
        if service_date_str:
            try:
                incident_date_obj = datetime.strptime(service_date_str, "%Y-%m-%d").date()
            except ValueError:
                incident_date_obj = claim_date_obj - timedelta(days=1)
        else:
            incident_date_obj = claim_date_obj - timedelta(days=1)
        
    else:
        # Standard database API format
        policy_id = int(data.get("policy_id"))
        claim_amount = float(data.get("claim_amount"))
        claim_type = data.get("claim_type", "Medical")
        diagnosis = data.get("diagnosis_code", "I10").strip()
        incident_desc = data.get("incident_description", "")
        incident_loc = data.get("incident_location", "")
        police_report = int(data.get("police_report_available", 0))
        witnesses = int(data.get("witnesses_count", 0))
        procedure = int(data.get("procedure_code") or 99213)
        length_of_stay = int(data.get("length_of_stay") or 2)
        hospital = data.get("provider_name") or "General Hospital"
        
        claim_date_str = data.get("claim_date")
        claim_date_obj = datetime.strptime(claim_date_str, "%Y-%m-%d").date()
        
        incident_date_str = data.get("incident_date")
        if incident_date_str:
            incident_date_obj = datetime.strptime(incident_date_str, "%Y-%m-%d").date()
        else:
            incident_date_obj = claim_date_obj - timedelta(days=1)

    # Generate unique claim number
    claim_num = f"CLM-{random.randint(100000, 999999)}"
    
    # Create Claim object
    claim = InsuranceClaim(
        claim_number=claim_num,
        policy_id=policy_id,
        claim_date=claim_date_obj,
        incident_date=incident_date_obj,
        claim_type=claim_type,
        claim_amount=claim_amount,
        incident_location=incident_loc,
        incident_description=incident_desc,
        police_report_available=police_report,
        witnesses_count=witnesses,
        claim_status="submitted",
        submitted_by=user_id,
        diagnosis_code=diagnosis,
        procedure_code=str(procedure),
        provider_name=hospital,
        length_of_stay=length_of_stay,
        visit_type="Inpatient" if length_of_stay > 0 else "Outpatient"
    )
    
    # Insert Claim to generate ID
    claim = db_save_claim(claim)
    
    # Log Audit: claim creation
    log_event(
        action="CLAIM_CREATION",
        user_id=user_id,
        claim_id=claim.claim_id,
        details=f"Claim {claim_num} created for policy ID {policy_id} with amount ${claim_amount:,.2f}."
    )

    # 2. Prepare payload for Machine Learning Predictor
    # Join with policy details for inference
    policy_obj = find_policy_by_id(policy_id)
    holder_obj = find_policyholder_by_id(policy_obj.policyholder_id)
    
    # Handle dates correctly
    dob = holder_obj.date_of_birth
    if isinstance(dob, str):
        try:
            dob = datetime.strptime(dob, "%Y-%m-%d").date()
        except ValueError:
            dob = None

    # Calculate actual age or fallback to input
    if dob:
        calculated_age = int((date.today() - dob).days / 365.25)
    else:
        calculated_age = int(data.get("age", 45))

    # Infer specialty dynamically based on procedure CPT code
    proc_code = int(claim.procedure_code or 99213)
    def infer_specialty(p_code):
        code_str = str(p_code)
        if code_str.startswith("7"):
            return "Radiology"
        elif code_str.startswith("93") or code_str.startswith("94"):
            return "Cardiology"
        elif code_str.startswith("99"):
            return "General Practice"
        else:
            return "Internal Medicine"
            
    specialty = infer_specialty(proc_code)

    # Dynamic count of claims for this provider monthly
    provider_monthly_claims = 30 # default fallback
    try:
        from repositories.claim_repository import count_claims_for_provider_monthly
        provider_monthly_claims = count_claims_for_provider_monthly(claim.provider_name)
        if provider_monthly_claims == 0:
            provider_monthly_claims = 30 # fallback if first claim
    except Exception as e:
        logger.warning(f"Error querying provider monthly claims: {e}")

    # Dynamic count of claims for this policyholder in last 12m
    prior_visits = 1 # default fallback
    try:
        from repositories.claim_repository import count_claims_last_12m_by_policy
        prior_visits = count_claims_last_12m_by_policy(policy_id)
        if prior_visits == 0:
            prior_visits = 1
    except Exception as e:
        logger.warning(f"Error querying claims last 12m: {e}")

    ml_payload = {
        "Patient_Age": calculated_age,
        "Patient_Gender": holder_obj.gender or "Male",
        "Diagnosis_Code": claim.diagnosis_code or "I10",
        "Procedure_Code": proc_code,
        "Claim_Amount": claim.claim_amount,
        "Approved_Amount": claim.claim_amount * 0.8, # 80% approved amount prediction helper
        "Insurance_Type": policy_obj.insurance_type or "Private",
        "Days_Between_Service_and_Claim": (claim.claim_date - claim.incident_date).days if isinstance(claim.claim_date, (date, datetime)) and isinstance(claim.incident_date, (date, datetime)) else 1,
        "Number_of_Claims_Per_Provider_Monthly": provider_monthly_claims,
        "Provider_Specialty": specialty,
        "Patient_State": holder_obj.state or "TX",
        "Claim_Status": "Pending",
        "Length_of_Stay": claim.length_of_stay,
        "Visit_Type": claim.visit_type or "Outpatient",
        "Chronic_Condition_Flag": 0,
        "Prior_Visits_12m": prior_visits
    }

    # Execute ML scoring & save prediction record
    prediction_result = run_claim_prediction(claim.claim_id, ml_payload)
    
    # Instantiate and assign prediction on the claim object
    claim.prediction = FraudPrediction(
        claim_id=claim.claim_id,
        predicted_label=prediction_result["predicted_label"],
        fraud_probability=prediction_result["fraud_probability"],
        raw_probability=prediction_result.get("raw_probability", 0.0),
        business_rule_adjustment=prediction_result.get("business_rule_adjustment", 0.0),
        risk_level=prediction_result["risk_level"],
        model_version=prediction_result["model_version"],
        remarks=", ".join(prediction_result["reasons"])
    )
    
    # 3. Apply Business Rules Engine based on prediction risk score
    # Auto Approve (0-30%)
    prob = prediction_result["fraud_probability"]
    
    if prob < 0.30:
        claim.claim_status = "approved"
        log_event(
            action="CLAIM_AUTO_APPROVAL",
            claim_id=claim.claim_id,
            details=f"Claim {claim_num} auto-approved (probability {prob*100:.2f}% < 30%)."
        )
    else:
        claim.claim_status = "under_review"
        log_event(
            action="CLAIM_ROUTE_FOR_REVIEW",
            claim_id=claim.claim_id,
            details=f"Claim {claim_num} routed for review (probability {prob*100:.2f}%, risk={prediction_result['risk_level']})."
        )
        
    db_save_claim(claim)

    # 4. Generate Notifications
    if claim.submitted_by:
        status_disp = claim.claim_status.upper()
        cust_msg = f"Claim {claim_num} submitted successfully. Current status: {status_disp}."
        send_notification(recipient_id=claim.submitted_by, message=cust_msg, severity="info" if claim.claim_status == "approved" else "warning")

    if claim.claim_status == "under_review":
        officers = find_users_by_role("employee")
        risk_disp = prediction_result["risk_level"].upper()
        officer_msg = f"New flagged claim {claim_num} requires manual review. Risk Level: {risk_disp}."
        for officer in officers:
            send_notification(recipient_id=officer.user_id, message=officer_msg, severity="warning" if risk_disp == "HIGH" else "info")

    return claim


def update_claim_status_service(claim_id: int, new_status: str, user_id: int) -> tuple[bool, str]:
    """
    Updates the status of a claim and records a corresponding audit event.
    """
    claim = find_claim_by_id(claim_id)
    if not claim:
        return False, "Claim not found"

    allowed_statuses = {"submitted", "under_review", "approved", "rejected"}
    if new_status not in allowed_statuses:
        return False, f"Invalid status. Allowed values are: {', '.join(allowed_statuses)}"

    old_status = claim.claim_status
    claim.claim_status = new_status
    db_save_claim(claim)

    # Log status change audit
    log_event(
        action=f"CLAIM_{new_status.upper()}",
        user_id=user_id,
        claim_id=claim.claim_id,
        details=f"Status changed from '{old_status}' to '{new_status}'."
    )

    # Send notification to the user who submitted the claim
    if claim.submitted_by:
        status_disp = new_status.upper()
        cust_msg = f"Your claim {claim.claim_number} status has been updated to {status_disp}."
        send_notification(
            recipient_id=claim.submitted_by,
            message=cust_msg,
            severity="info" if new_status == "approved" else ("warning" if new_status == "rejected" else "info")
        )

    return True, f"Claim status updated to {new_status} successfully."
