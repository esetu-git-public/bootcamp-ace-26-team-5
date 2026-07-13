import numpy as np

def generate_explainability_report(normalized: dict, prob: float, risk_level: str) -> dict:
    """
    Formulates a structured explainability payload.
    
    Note: The confidence represents an "Estimated Confidence" derived from the prediction 
    uncertainty margin relative to the 0.5 classification boundary, rather than a formally 
    calibrated classifier calibration (e.g., Platt scaling).
    
    Args:
        normalized (dict): Features dictionary containing engineered values.
        prob (float): Model classification probability (0.0 to 1.0).
        risk_level (str): Calculated risk mapping level ("Low", "Medium", "High").
        
    Returns:
        dict: Detailed auditor inspector statistics.
    """
    # 1. Calculate Estimated Confidence based on distance from the 0.5 classification threshold
    margin = abs(prob - 0.5) * 2.0  # Normalized distance: 0.0 at prob=0.5, 1.0 at prob=0 or 1
    # Scale non-linearly to provide a realistic uncertainty curve
    estimated_conf_pct = (0.5 + 0.5 * (margin ** 0.5)) * 100.0
    estimated_conf_pct = round(min(max(estimated_conf_pct, 50.0), 99.99), 2)

    # 2. Extract input values for indicator analysis
    claim_amount = normalized.get("Claim_Amount", 0.0)
    stay_days = normalized.get("Length_of_Stay", 0)
    provider_load = normalized.get("Number_of_Claims_Per_Provider_Monthly", 0)
    visits = normalized.get("Prior_Visits_12m", 0)
    chronic_flag = normalized.get("Chronic_Condition_Flag", 0)
    approval_ratio = normalized.get("Approval_Ratio", 1.0)
    
    # Percentile thresholds from training references
    claim_thresh = 711.365
    provider_thresh = 72.0

    # 3. Analyze promoters/mitigators (positive/negative indicators)
    pos_indicators = []
    neg_indicators = []
    reasons = []

    # Claim Size Analysis
    if claim_amount > claim_thresh:
        neg_indicators.append(f"Elevated claim size (${claim_amount:,.2f})")
        reasons.append(f"High claim amount (${claim_amount:,.2f} > normal threshold ${claim_thresh:,.2f})")
    else:
        pos_indicators.append(f"Acceptable claim size (${claim_amount:,.2f})")

    # Length of Stay Analysis
    if stay_days >= 7:
        neg_indicators.append(f"Prolonged hospital stay duration ({stay_days} days)")
        reasons.append(f"Unusual hospital stay duration ({stay_days} days)")
    else:
        pos_indicators.append(f"Normal hospital stay duration ({stay_days} days)")

    # Provider Volumetrics
    if provider_load > provider_thresh:
        neg_indicators.append(f"High provider activity density ({provider_load} claims/month)")
        reasons.append(f"High monthly claims volume for provider ({provider_load} claims)")
    else:
        pos_indicators.append(f"Standard provider claims frequency ({provider_load} claims/month)")

    # Visit Frequency
    if visits >= 5:
        neg_indicators.append(f"Frequent patient claims record ({visits} visits)")
        reasons.append(f"High frequent visits count ({visits} visits in last 12m)")
    else:
        pos_indicators.append(f"Normal patient medical history density ({visits} visits in last 12m)")

    # Historical Approval Ratio
    if approval_ratio < 0.70:
        neg_indicators.append(f"High patient claims rejection history (approval ratio {approval_ratio*100:.1f}%)")
    else:
        pos_indicators.append(f"Acceptable amount approval ratio ({approval_ratio*100:.1f}%)")

    # Chronic Conditions Flag
    if chronic_flag > 0:
        neg_indicators.append(f"Patient has active chronic health conditions")
    else:
        pos_indicators.append("No chronic health flags")

    # 4. Formulate Recommended Actions and Reviewer Notes
    if risk_level == "Low":
        rec_action = "Auto-Approve Claim"
        notes = f"The claim was successfully evaluated as Low Risk ({prob*100:.1f}% probability). No major billing anomalies detected."
        advice = "No manual investigation required. Claim meets standard risk profiles. Proceed with auto-approval."
        explanation = f"This claim was evaluated as Low Risk with a fraud probability of {prob*100:.1f}%. The billing parameters are within acceptable bounds, and there are no signs of billing anomalies."
    elif risk_level == "Medium":
        rec_action = "Route to Secondary Audit Queue"
        notes = f"Model flags claim under Medium Risk ({prob*100:.1f}% probability). Minor billing anomalies or slightly elevated claim size detected. Recommended for standard review."
        advice = "Verify itemized billing statements, patient history, and prior visits. Confirm validity of length of stay and approval ratio."
        explanation = f"The claim was classified as Medium Risk with a fraud probability of {prob*100:.1f}%. This is driven by minor billing anomalies or slightly elevated claim size. Standard review is recommended."
    else:
        rec_action = "Escalate to Fraud Investigation Unit (FIU)"
        notes = f"High Risk Alert ({prob*100:.1f}% probability). The claim demonstrates high billing frequency, abnormal stay duration, or large claim size. Immediate audit required."
        advice = "Perform complete audit. Contact healthcare provider to verify treatments. Cross-reference diagnosis codes with length of stay, and check prior claims for patterns of over-billing."
        explanation = f"CRITICAL ALERT: This claim was flagged as High Risk with a fraud probability of {prob*100:.1f}%. It exhibits multiple severe risk promoters, including abnormal stay duration, elevated claim size, or high provider volume."

    # 5. Define Feature Importance values (simulated based on model weights)
    feat_importance = {
        "Claim_Amount": 0.35,
        "Approval_Ratio": 0.05,
        "Length_of_Stay": 0.15,
        "Number_of_Claims_Per_Provider_Monthly": 0.15,
        "Prior_Visits_12m": 0.10,
        "Other_Categorical_Features": 0.20
    }

    reasons_list = reasons if reasons else ["No prominent risk factors flagged"]

    return {
        "fraud_probability": round(prob * 100.0, 2),
        "probability": round(prob, 4),
        "risk_level": risk_level,
        "prediction_confidence": estimated_conf_pct,
        "top_risk_factors": reasons_list,
        "top_reasons": reasons_list,
        "feature_importance": feat_importance,
        "feature_contributions": feat_importance,
        "recommended_action": rec_action,
        "recommendation": rec_action,
        "reviewer_notes": notes,
        "investigation_advice": advice,
        "human_readable_explanation": explanation,
        "positive_indicators": pos_indicators,
        "negative_indicators": neg_indicators
    }
