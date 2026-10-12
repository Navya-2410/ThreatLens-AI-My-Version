
import re
from rapidfuzz import fuzz


def normalize_name(value):
    """Normalize a username or profile name for comparison."""
    value = str(value or "").lower().strip()
    value = value.replace("@", "")
    return re.sub(r"[^a-z0-9]", "", value)


def detect_social_profiles(official_accounts, candidates):
    """
    Compare candidate social profiles against registered official accounts.

    official_accounts example:
        [{"username": "novabank", "name": "Nova Bank"}]

    candidates example:
        [{"username": "novabannk", "name": "Nova Bank Support"}]

    Returns a list of explainable detection results.
    """

    results = []

    for candidate in candidates:
        candidate_username = normalize_name(
            candidate.get("username", "")
        )
        candidate_name = normalize_name(
            candidate.get("name", "")
        )

        # Exclude registered official accounts first.
        is_official = False

        for official in official_accounts:
            official_username = normalize_name(
                official.get("username", "")
            )

            if (
                candidate_username
                and official_username
                and candidate_username == official_username
            ):
                is_official = True
                break

        if is_official:
            results.append({
                "username": candidate.get("username", ""),
                "name": candidate.get("name", ""),
                "risk_score": 0,
                "risk_level": "Official",
                "is_official": True,
                "reasons": ["Matches a registered official username."]
            })
            continue

        best_username_similarity = 0
        best_name_similarity = 0
        reasons = []

        # Find the closest registered brand/profile.
        for official in official_accounts:
            official_username = normalize_name(
                official.get("username", "")
            )
            official_name = normalize_name(
                official.get("name", "")
            )

            if candidate_username and official_username:
                similarity = fuzz.ratio(
                    candidate_username, official_username
                )
                best_username_similarity = max(
                    best_username_similarity, similarity
                )

            if candidate_name and official_name:
                similarity = fuzz.ratio(
                    candidate_name, official_name
                )
                best_name_similarity = max(
                    best_name_similarity, similarity
                )

        score = 0

        if best_username_similarity >= 90:
            score += 55
            reasons.append("Username is very similar to an official username.")
        elif best_username_similarity >= 75:
            score += 35
            reasons.append("Username resembles an official username.")

        if best_name_similarity >= 90:
            score += 35
            reasons.append("Profile name closely resembles the official name.")
        elif best_name_similarity >= 75:
            score += 20
            reasons.append("Profile name is similar to the official name.")

        # Extra words may be relevant, but are not proof of fraud.
        extra_terms = (
            "support", "help", "security", "verify",
            "claim", "bonus", "customer"
        )

        username = str(candidate.get("username", "")).lower()
        profile_name = str(candidate.get("name", "")).lower()
        combined_text = username + " " + profile_name

        if any(term in combined_text for term in extra_terms):
            score += 10
            reasons.append("Contains an extra support or verification-related term.")

        score = min(score, 100)

        if score >= 70:
            risk_level = "High"
        elif score >= 35:
            risk_level = "Medium"
        else:
            risk_level = "Low"

        if not reasons:
            reasons.append("No strong look-alike signals detected.")

        results.append({
            "username": candidate.get("username", ""),
            "name": candidate.get("name", ""),
            "risk_score": score,
            "risk_level": risk_level,
            "is_official": False,
            "username_similarity": round(
                best_username_similarity, 1
            ),
            "name_similarity": round(
                best_name_similarity, 1
            ),
            "reasons": reasons
        })

    return results