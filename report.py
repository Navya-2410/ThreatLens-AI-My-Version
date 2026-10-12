import json
from datetime import datetime


def generate_report(results, filename="threat_report.json"):
    """
    Save threat detection results to a JSON report.
    """
    report = {
        "project": "ThreatLens AI",
        "generated_at": datetime.now().isoformat(
            timespec="seconds"
        ),
        "total_items_scanned": len(results),
        "flagged_items": sum(
            1 for item in results
            if item.get("risk_level") in ("Medium", "High")
        ),
        "results": results
    }

    with open(filename, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=4, ensure_ascii=False)

    return report

if __name__ == "__main__":
    sample_results = [
        {"name": "NovaKart Shopping", "risk_level": "High"},
        {"name": "Safe Example App", "risk_level": "Low"}
    ]

    result = generate_report(sample_results)
    print(result)
    print("Report saved successfully!")
