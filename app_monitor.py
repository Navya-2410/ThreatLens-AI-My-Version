
from rapidfuzz.fuzz import ratio
from risk_scorer import calculate_risk


def monitor_apps(brand_profile, app_listings):
    findings = []

    official_app = brand_profile.get("official_app", {})
    official_name = official_app.get("name", "")
    official_developer = official_app.get("developer", "")

    if not official_name:
        official_name = brand_profile.get("brand_name", "")

    for app in app_listings:
        app_name = app.get("name", "")
        developer = app.get("developer", "")
        description = app.get("description", "")

        official_description = official_app.get("description", "")

        # Exclude the official app when both name and developer match.
        if (
            app_name.strip().lower() == official_name.strip().lower()
            and developer.strip().lower()
            == official_developer.strip().lower()
            and official_name.strip()
            and official_developer.strip()
        ):
            continue

        name_similarity = ratio(
            official_name.lower(),
            app_name.lower()
        ) if official_name and app_name else 0

        description_similarity = ratio(
            official_description.lower(),
            description.lower()
        ) if official_description and description else 0

        publisher_mismatch = bool(
            official_developer
            and developer
            and developer.strip().lower()
            != official_developer.strip().lower()
        )

        risk = calculate_risk(
            name_similarity=name_similarity,
            publisher_mismatch=publisher_mismatch,
            description_similarity=description_similarity
        )

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
