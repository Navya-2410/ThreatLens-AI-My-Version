
from rapidfuzz.fuzz import ratio


def monitor_social_profiles(brand_profile, profiles):
    findings = []

    brand_name = brand_profile.get("brand_name", "")
    official_accounts = brand_profile.get("social_accounts", {})

    official_values = [
        str(value).strip().lower()
        for value in official_accounts.values()
        if value and str(value).strip()
    ]

    for profile in profiles:
        name = profile.get("name", "")
        username = profile.get("username", "")
        platform = profile.get("platform", "Unknown")
        account_url = profile.get("url", "")

        # Exclude registered official accounts.
        account_details = [
            str(username).strip().lower(),
            str(account_url).strip().lower()
        ]

        if any(value in official_values for value in account_details):
            continue

        name_score = (
            ratio(brand_name.lower(), name.lower())
            if brand_name and name else 0
        )

        username_score = (
            ratio(
                brand_name.lower().replace(" ", ""),
                username.lower().replace("@", "").replace("_", "")
            )
            if brand_name and username else 0
        )

        score = 0
        reasons = []

        if name_score >= 90:
            score += 40
            reasons.append("Very high brand-name similarity")
        elif name_score >= 75:
            score += 25
            reasons.append("High brand-name similarity")
        elif name_score >= 50:
            score += 10
            reasons.append("Moderate brand-name similarity")

        if username_score >= 85:
            score += 25
            reasons.append("Username resembles the brand name")

        score = min(score, 100)

        if score >= 70:
            level = "High"
        elif score >= 30:
            level = "Medium"
        else:
            level = "Low"

        if not reasons:
            reasons.append("No strong risk indicators found")

        findings.append({
            "name": name,
            "username": username,
            "platform": platform,
            "url": account_url,
            "risk_score": score,
            "risk_level": level,
            "reasons": reasons
        })

    return findings
