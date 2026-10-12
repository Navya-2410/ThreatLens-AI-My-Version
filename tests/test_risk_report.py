from risk_scorer import calculate_risk
from report import generate_report


def test_high_risk_candidate():
    risk = calculate_risk(95, True, 85, False)

    assert risk["risk_score"] == 85
    assert risk["risk_level"] == "High"


def test_low_risk_candidate():
    risk = calculate_risk(20, False, 10, False)

    assert risk["risk_score"] == 0
    assert risk["risk_level"] == "Low"


def test_report_counts_flagged_items(tmp_path):
    results = [
        {
            "name": "Suspicious App",
            "risk_score": 85,
            "risk_level": "High",
            "reasons": ["High name similarity"],
        },
        {
            "name": "Safe Example",
            "risk_score": 0,
            "risk_level": "Low",
            "reasons": ["No strong risk indicators found"],
        },
    ]

    output_file = tmp_path / "test_report.json"
    report = generate_report(results, str(output_file))

    assert report["total_items_scanned"] == 2
    assert report["flagged_items"] == 1
    assert output_file.exists()