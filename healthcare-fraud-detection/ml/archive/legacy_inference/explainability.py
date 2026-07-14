from ml.inference.feature_engineering import _claim_threshold, _provider_threshold

def generate_explainability_report(raw_data: dict, prob: float, risk_level: str) -> dict:
    """
    Compiles detailed explainability matrices, including positive/negative indicators,
    feature importance, recommended actions, and reviewer notes.
    """
    claim_amount = float(raw_data.get("Claim_Amount", 0))
    approved_amount = float(raw_data.get("Approved_Amount", 0))
    stay = int(raw_data.get("Length_of_Stay", 0))
    visits = int(raw_data.get("Prior_Visits_12m", 0))
    provider_claims = int(raw_data.get("Number_of_Claims_Per_Provider_Monthly", 0))
    chronic_flag = int(raw_data.get("Chronic_Condition_Flag", 0))
    witnesses = int(raw_data.get("witnesses_count", 0))
    police_report = int(raw_data.get("police_report_available", 0))
    
    ratio = (approved_amount / claim_amount) if claim_amount > 0 else 1.0

    top_risk_factors = []
    positive_indicators = []
    negative_indicators = []
    feature_importance = {}

    # 1. Evaluate Risk Indicators & Top Factors
    if claim_amount > _claim_threshold:
        top_risk_factors.append(f"High claim amount (${claim_amount:,.2f} > normal threshold ${_claim_threshold:,.2f})")
        negative_indicators.append("Elevated claim size")
        feature_importance["Claim_Amount"] = 0.35
    else:
        positive_indicators.append("Claim size within normal boundaries")
        feature_importance["Claim_Amount"] = 0.05

    if ratio < 0.50:
        top_risk_factors.append(f"Low approved ratio (only {ratio*100:.1f}% approved)")
        negative_indicators.append("High amount deduction discrepancy")
        feature_importance["Approval_Ratio"] = 0.25
    else:
        positive_indicators.append("Acceptable amount approval ratio")
        feature_importance["Approval_Ratio"] = 0.05

    if stay >= 7:
        top_risk_factors.append(f"Unusual hospital stay duration ({stay} days)")
        negative_indicators.append("Prolonged stay length")
        feature_importance["Length_of_Stay"] = 0.15
    else:
        positive_indicators.append("Standard stay duration")
        feature_importance["Length_of_Stay"] = 0.02

    if provider_claims > _provider_threshold:
        top_risk_factors.append(f"High monthly claims volume for provider ({provider_claims} claims)")
        negative_indicators.append("High provider activity density")
        feature_importance["Number_of_Claims_Per_Provider_Monthly"] = 0.15
    else:
        positive_indicators.append("Stable provider claims activity")
        feature_importance["Number_of_Claims_Per_Provider_Monthly"] = 0.02

    if visits >= 5:
        top_risk_factors.append(f"High frequent visits count ({visits} visits in last 12m)")
        negative_indicators.append("Frequent patient claims record")
        feature_importance["Prior_Visits_12m"] = 0.10
    else:
        positive_indicators.append("Normal patient visit frequency")
        feature_importance["Prior_Visits_12m"] = 0.01

    if chronic_flag == 1:
        negative_indicators.append("Chronic condition diagnosis present")
    else:
        positive_indicators.append("No chronic health flags")

    if police_report == 1 or witnesses > 0:
        positive_indicators.append("Supporting accident evidence reported (police report/witnesses)")

    # 2. Estimate remaining importance weights
    tot_weight = sum(feature_importance.values())
    if tot_weight < 1.0:
        feature_importance["Other_Categorical_Features"] = round(1.0 - tot_weight, 2)

    # 3. Formulate Suggested Action & Notes
    if risk_level == "Low":
        recommended_action = "Auto-Approve Claim"
        reviewer_notes = f"The claim was successfully evaluated as Low Risk ({prob*100:.1f}% probability). No major anomalies detected."
    elif risk_level == "Medium":
        recommended_action = "Route for Auditing"
        reviewer_notes = (
            f"Evaluated as Medium Risk ({prob*100:.1f}% probability). Minor irregularities found: "
            f"{', '.join(top_risk_factors) if top_risk_factors else 'Co-occurrence pattern suspicious'}. Audit recommended."
        )
    else:
        recommended_action = "Escalate to Claim Inspector Queue"
        reviewer_notes = (
            f"CRITICAL: Flagged as High Risk ({prob*100:.1f}% probability). Severe anomalies identified: "
            f"{'; '.join(top_risk_factors)}. Immediate manual inspection required."
        )

    # Calculate probability-relative confidence
    confidence = float(1 - prob if prob < 0.50 else prob)

    # Return consolidated payload formatting probabilities and confidence as percentages (0-100)
    return {
        "fraud_probability": round(prob * 100, 2),
        "risk_level": risk_level,
        "prediction_confidence": round(confidence * 100, 2),
        "top_risk_factors": top_risk_factors if top_risk_factors else ["Procedure code co-occurrence metrics"],
        "feature_importance": feature_importance,
        "positive_indicators": positive_indicators,
        "negative_indicators": negative_indicators,
        "recommended_action": recommended_action,
        "reviewer_notes": reviewer_notes
    }
