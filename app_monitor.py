from rapidfuzz.fuzz import ratio, token_set_ratio

from risk_scorer import calculate_risk


def _normalize_name(value):
    """Lowercase a name and remove spaces and punctuation."""
    return "".join(
        character
        for character in str(value or "").lower()
        if character.isalnum()
    )


def monitor_apps(brand_profile, app_listings):
    """Return app listings with medium or high impersonation risk."""
    findings = []

    official_app = brand_profile.get("official_app", {})
    official_name = official_app.get("name", "")
    official_developer = official_app.get("developer", "")
    official_description = official_app.get("description", "")

    if not official_name:
        official_name = brand_profile.get("brand_name", "")

    for app in app_listings:
        app_name = app.get("name", "")
        developer = app.get("developer", "")
        description = app.get("description", "")

        official_name_normalized = _normalize_name(official_name)
        app_name_normalized = _normalize_name(app_name)

        official_developer_normalized = _normalize_name(official_developer)
        developer_normalized = _normalize_name(developer)

        # Exclude the official app when its name and publisher match.
        if (
            official_name_normalized
            and official_developer_normalized
            and app_name_normalized == official_name_normalized
            and developer_normalized == official_developer_normalized
        ):
            continue

        publisher_mismatch = bool(
            official_developer_normalized
            and developer_normalized
            and developer_normalized != official_developer_normalized
        )

        description_similarity = (
            ratio(
                official_description.lower(),
                description.lower()
            )
            if official_description and description
            else 0
        )

        # Normalized comparison catches spacing and small character changes.
        basic_name_similarity = (
            ratio(official_name_normalized, app_name_normalized)
            if official_name_normalized and app_name_normalized
            else 0
        )

        # Token comparison can catch added words, such as "ThreatLens AI Pro".
        # Use it only when another signal supports the match.
        if publisher_mismatch or description_similarity >= 60:
            name_similarity = max(
                basic_name_similarity,
                token_set_ratio(official_name.lower(), app_name.lower())
            )
        else:
            name_similarity = basic_name_similarity

        risk = calculate_risk(
            name_similarity=name_similarity,
            publisher_mismatch=publisher_mismatch,
            description_similarity=description_similarity
        )

        # Return medium- and high-risk findings; skip low-risk listings.
        if risk["risk_score"] < 30:
            continue

        findings.append({
            "name": app_name,
            "developer": developer,
            "description": description,
            "store": app.get("store", "Sample data"),
            "url": app.get("url", ""),
            "name_similarity": round(name_similarity, 2),
            "risk_score": risk["risk_score"],
            "risk_level": risk["risk_level"],
            "reasons": risk["reasons"]
        })

    return findings