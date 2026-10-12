
import re
from rapidfuzz import fuzz


SUSPICIOUS_TERMS = (
    "support",
    "help",
    "security",
    "verify",
    "claim",
    "bonus",
    "customer",
)


def normalize_name(value):
    """Normalize names and usernames for comparison."""
    value = str(value or "").lower().strip()
    value = value.replace("@", "")
    return re.sub(r"[^a-z0-9]", "", value)


def _extract_username(value):
    """Extract a username from a handle or profile URL."""
    value = str(value or "").strip()

    if not value:
        return ""

    if value.startswith("@"):
        return value[1:]

    if "://" in value:
        value = value.rstrip("/").split("/")[-1]

    return value.lstrip("@").strip()


def _contains_suspicious_term(*values):
    """Check for suspicious terms as separate username/name tokens."""
    for value in values:
        words = re.findall(r"[a-z0-9]+", str(value or "").lower())
        if any(word in SUSPICIOUS_TERMS for word in words):
            return True
    return False


def monitor_social_profiles(brand_profile, profiles):
    """Score supplied candidate profiles for possible impersonation."""

    findings = []

    brand_name = str(brand_profile.get("brand_name", "") or "")
    social_accounts = brand_profile.get("social_accounts", {}) or {}

    normalized_brand = normalize_name(brand_name)
    brand_tokens = {
        normalize_name(token)
        for token in re.findall(r"[a-z0-9]+", brand_name.lower())
        if normalize_name(token)
    }
    official_usernames = set()
    official_urls = set()

    for value in social_accounts.values():
        if not value:
            continue

        value = str(value).strip()

        if value.startswith("@"):
            official_usernames.add(normalize_name(value))
        elif "://" in value:
            official_urls.add(value.lower().rstrip("/"))
        else:
                        official_usernames.add(normalize_name(value))

    for profile in profiles:
        name = str(profile.get("name", "") or "")
        username = str(profile.get("username", "") or "")
        account_url = str(profile.get("url", "") or "")
        platform = profile.get("platform", "Unknown")

        normalized_name = normalize_name(name)
        normalized_username = normalize_name(username)
        normalized_url = account_url.lower().rstrip("/")

        # Exclude known official handles and exact official URLs.
        if (
            normalized_username
            and normalized_username in official_usernames
        ) or (
            normalized_url
            and normalized_url in official_urls
        ):
            continue

        # Compare the complete name and username after normalization.
        name_similarity = (
            fuzz.ratio(normalized_brand, normalized_name)
            if normalized_brand and normalized_name
            else 0
        )
        username_similarity = (
            fuzz.ratio(normalized_brand, normalized_username)
            if normalized_brand and normalized_username
            else 0
        )

        # Token-based matching helps when extra words are added.
        name_token_similarity = (
            fuzz.token_set_ratio(brand_name, name)
            if brand_name and name
            else 0
        )
        username_token_similarity = (
            fuzz.token_set_ratio(brand_name, username)
            if brand_name and username
            else 0
        )

        # Use the strongest relevant similarity signal.
        name_similarity = max(name_similarity, name_token_similarity)
        username_similarity = max(
            username_similarity, username_token_similarity
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

        # Extra words increase risk only when the account also resembles
        # the brand. This reduces false positives from unrelated accounts.
        has_suspicious_term = _contains_suspicious_term(name, username)
        resembles_brand = (
            name_similarity >= 50 or username_similarity >= 50
        )

        if has_suspicious_term and resembles_brand:
            score += 10
            reasons.append(
                "Brand-like account contains a support or verification term"
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
    """Compatibility wrapper for the existing function interface."""

    brand_profile = {
        "brand_name": "",
        "social_accounts": {}
    }

    for official in official_accounts:
        platform = official.get("platform", "other")
        brand_profile["social_accounts"][platform] = (
            official.get("url") or official.get("username", "")
        )

        if not brand_profile["brand_name"]:
            brand_profile["brand_name"] = official.get("name", "")

    return monitor_social_profiles(brand_profile, candidates)