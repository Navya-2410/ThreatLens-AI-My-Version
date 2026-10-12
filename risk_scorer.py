def calculate_risk(name_similarity, publisher_mismatch=False,
                   description_similarity=0, logo_match=False):
    """
    Calculate an explainable risk score from 0 to 100.

    Similarity values must be between 0 and 100.
    This is a prototype heuristic, not proof of fraud.
    """
    score = 0
    reasons = []

    # Similar names may indicate impersonation.
    if name_similarity >= 90:
        score += 40
        reasons.append("Very high name similarity")
    elif name_similarity >= 75:
        score += 25
        reasons.append("High name similarity")
    elif name_similarity >= 50:
        score += 10
        reasons.append("Moderate name similarity")

    # A different publisher can be a warning sign.
    if publisher_mismatch:
        score += 25
        reasons.append("Publisher differs from the official publisher")

    # Similar descriptions may indicate copied branding.
    if description_similarity >= 80:
        score += 20
        reasons.append("Description closely resembles the official description")
    elif description_similarity >= 60:
        score += 10
        reasons.append("Description has some similarity")

    # A matching logo alone is not proof of impersonation.
    if logo_match:
        score += 15
        reasons.append("Logo resembles the official logo")

    score = min(score, 100)

    if score >= 70:
        level = "High"
    elif score >= 30:
        level = "Medium"
    else:
        level = "Low"

    if not reasons:
        reasons.append("No strong risk indicators found")

    return {
        "risk_score": score,
        "risk_level": level,
        "reasons": reasons
    }
