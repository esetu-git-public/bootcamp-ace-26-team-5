def generate_reasons(claim_data):

    reasons = []

    if claim_data.get("Claim_Amount", 0) > 700:
        reasons.append("High Claim Amount")

    if claim_data.get("Prior_Visits_12m", 0) >= 5:
        reasons.append("Frequent Previous Visits")

    if claim_data.get("Length_of_Stay", 0) >= 7:
        reasons.append("Long Hospital Stay")

    if claim_data.get("Number_of_Claims_Per_Provider_Monthly", 0) >= 70:
        reasons.append("High Provider Claim Volume")

    if not reasons:
        reasons.append("No significant fraud indicators detected.")

    return reasons