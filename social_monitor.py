
import re
from rapidfuzz import fuzz


def normalize_name(value):
    """Normalize names and usernames for comparison."""
    value = str(value or "").lower().strip()
    value = value.replace("@", "")
    return re.sub(r"[^a-z0-9]", "", value)


def monitor_social_profiles(brand_profile, profiles):
    """Find possible social profile impersonation using sample data."""

    findings = []

    brand_name = brand_profile.get("brand_name", "")
    social_accounts = brand_profile.get("social_accounts", {})

    official_accounts = []

    for platform, value in social_accounts.items():
        if not value or not str(value).strip():
            continue

        value = str(value).strip()

        if value.startswith("@"):
            username = value
        else:
            username = value.rstrip("/").split("/")[-1]

        official_accounts.append({
            "username": username,
            "name": brand_name,
            "url": value,
            "platform": platform
        })

    normalized_brand = normalize_name(brand_name)

    for profile in profiles:
        name = profile.get("name", "")
        username = profile.get("username", "")
        account_url = profile.get("url", "")
        platform = profile.get("platform", "Unknown")

        normalized_username = normalize_name(username)
        normalized_name = normalize_name(name)

        # Exclude exact registered usernames or official URLs.
        is_official = False

        for official in official_accounts:
            official_username = normalize_name(
                official.get("username", "")
            )
            official_url = official.get("url", "").lower().rstrip("/")
            candidate_url = account_url.lower().rstrip("/")

            if (
                normalized_username
                and official_username
                and normalized_username == official_username
            ):
                is_official = True

            if candidate_url and official_url == candidate_url:
                is_official = True

        if is_official:
            continue

        name_similarity = (
            fuzz.ratio(normalized_brand, normalized_name)
            if normalized_brand and normalized_name else 0
        )

        username_similarity = (
            fuzz.ratio(normalized_brand, normalized_username)
            if normalized_brand and normalized_username else 0
        )

        score = 0
        reasons = []

        if name_similarity >= 90:
            score += 40
            reasons.append("Very high brand-name similarity")
        elif name_similarity >= 75:
            score += 25
            reasons.append("High brand-name similarity")
        elif name_similarity >= 50:
            score += 10
            reasons.append("Moderate brand-name similarity")

        if username_similarity >= 90:
            score += 35
            reasons.append("Username is very similar to the brand name")
        elif username_similarity >= 75:
            score += 20
            reasons.append("Username resembles the brand name")

        extra_terms = (
            "support", "help", "security", "verify",
            "claim", "bonus", "customer"
        )

        combined_text = (
            str(username).lower() + " " + str(name).lower()
        )

        if any(term in combined_text for term in extra_terms):
            score += 10
            reasons.append(
                "Contains a support or verification-related term"
            )

        score = min(score, 100)

        if score >= 70:
            risk_level = "High"
        elif score >= 30:
            risk_level = "Medium"
        else:
            risk_level = "Low"

        if not reasons:
            reasons.append("No strong look-alike signals detected")

        findings.append({
            "name": name,
            "username": username,
            "platform": platform,
            "url": account_url,
            "risk_score": score,
            "risk_level": risk_level,
            "name_similarity": round(name_similarity, 1),
            "username_similarity": round(username_similarity, 1),
            "is_official": False,
            "reasons": reasons
        })

    return findings


def detect_social_profiles(official_accounts, candidates):
    """Compatibility wrapper for the teammate's function interface."""

    brand_profile = {
        "brand_name": "",
        "social_accounts": {}
    }

    for official in official_accounts:
        platform = official.get("platform", "other")
        brand_profile["social_accounts"][platform] = (
            official.get("url")
            or official.get("username", "")
        )

        if not brand_profile["brand_name"]:
            brand_profile["brand_name"] = official.get("name", "")

    results = monitor_social_profiles(brand_profile, candidates)

    return results
