def generate_reasons(claim_data: dict) -> list[str]:
    """
    Generate natural language explainability reasons based on claim inputs.
    """
    reasons = []

    claim_amount = float(claim_data.get("Claim_Amount", 0))
    approved_amount = float(claim_data.get("Approved_Amount", claim_amount * 0.8))
    stay = int(claim_data.get("Length_of_Stay", 0))
    visits = int(claim_data.get("Prior_Visits_12m", 0))
    provider_claims = int(claim_data.get("Number_of_Claims_Per_Provider_Monthly", 0))
    claim_delay = int(claim_data.get("Days_Between_Service_and_Claim", 0))

    # Calculate Approval Ratio
    approval_ratio = approved_amount / (claim_amount + 1)

    if claim_amount > 700:
        reasons.append("High Claim Amount")

    if visits >= 5:
        reasons.append("Frequent Previous Visits")

    if stay >= 7:
        reasons.append("Long Hospital Stay")

    if provider_claims >= 70:
        reasons.append("High Provider Claim Volume")

    if claim_amount > 500 and approval_ratio < 0.5:
        reasons.append("Suspicious Low Approval Ratio")

    if claim_delay >= 30:
        reasons.append("Delayed Claim Submission")

    if not reasons:
        reasons.append("No significant fraud indicators detected.")

    return reasons
