def generate_reasons(claim_data: dict) -> list[str]:
    """
    Generate natural language explainability reasons based on claim inputs.
    """
    reasons = []

    claim_amount = float(claim_data.get("Claim_Amount", 0))
    stay = int(claim_data.get("Length_of_Stay", 0))
    visits = int(claim_data.get("Prior_Visits_12m", 0))
    provider_claims = int(claim_data.get("Number_of_Claims_Per_Provider_Monthly", 0))

    if claim_amount > 700:
        reasons.append("High Claim Amount")

    if visits >= 5:
        reasons.append("Frequent Previous Visits")

    if stay >= 7:
        reasons.append("Long Hospital Stay")

    if provider_claims >= 70:
        reasons.append("High Provider Claim Volume")

    if not reasons:
        reasons.append("No significant fraud indicators detected.")

    return reasons
