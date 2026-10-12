
import json
import unittest
from pathlib import Path

from app_monitor import monitor_apps


data_path = Path(__file__).resolve().parents[1] / "data" / "sample_data.json"
with data_path.open(encoding="utf-8") as file:
    sample_data = json.load(file)


class AppMonitorTests(unittest.TestCase):
    def setUp(self):
        self.brand_profile = sample_data["brand_profile"]
        self.app_listings = sample_data["app_listings"]
        self.findings = monitor_apps(self.brand_profile, self.app_listings)
        self.finding_names = {item["name"] for item in self.findings}

    def test_suspicious_lookalike_is_flagged(self):
        self.assertIn("ThreatLens Security", self.finding_names)

    def test_official_app_is_not_flagged(self):
        self.assertNotIn("ThreatLens AI", self.finding_names)

    def test_shopswift_official_app_is_not_flagged(self):
        brand = next(
            item for item in sample_data["brands"]
            if item["brand_name"] == "ShopSwift"
        )
        findings = monitor_apps(brand, self.app_listings)
        finding_names = {item["name"] for item in findings}

        self.assertNotIn("ShopSwift Shopping", finding_names)

    def test_unrelated_app_is_not_flagged(self):
        self.assertNotIn("Weather Today", self.finding_names)

    def test_finding_has_score_and_reasons(self):
        finding = next(
            item for item in self.findings
            if item["name"] == "ThreatLens Security"
        )
        self.assertGreaterEqual(finding["risk_score"], 45)
        self.assertTrue(finding["reasons"])


if __name__ == "__main__":
    unittest.main()