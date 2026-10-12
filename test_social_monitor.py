
from social_monitor import detect_social_profiles

official_accounts = [
    {
        "username": "novabank",
        "name": "Nova Bank"
    }
]

candidates = [
    {
        "username": "novabank",
        "name": "Nova Bank"
    },
    {
        "username": "novabannk",
        "name": "Nova Bank Support"
    },
    {
        "username": "randomphotography",
        "name": "Random Photography"
    },
    {
        "username": "",
        "name": ""
    },
    {
        "username": "novabank_support",
        "name": ""
    }
]

results = detect_social_profiles(
    official_accounts, candidates
)

for result in results:
    print("-" * 40)
    print("Username:", result["username"])
    print("Risk score:", result["risk_score"])
    print("Risk level:", result["risk_level"])
    print("Official:", result["is_official"])
    print("Reasons:", ", ".join(result["reasons"]))