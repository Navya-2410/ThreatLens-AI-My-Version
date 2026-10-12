
import unittest

from social_monitor import monitor_social_profiles


class SocialMonitorTests(unittest.TestCase):
    def setUp(self):
        self.brand = {
            "brand_name": "NovaBank",
            "social_accounts": {
                "instagram": "@novabank_official",
                "facebook": "https://facebook.com/novabank"
            }
        }

    def test_official_account_is_excluded(self):
        profiles = [{
            "name": "NovaBank",
            "username": "@novabank_official",
            "platform": "Instagram",
            "url": ""
        }]

        findings = monitor_social_profiles(self.brand, profiles)

        self.assertEqual(findings, [])

    def test_lookalike_username_is_detected(self):
        profiles = [{
            "name": "NovaBank Support",
            "username": "@novabannk",
            "platform": "Instagram",
            "url": "https://example.com/novabannk"
        }]

        findings = monitor_social_profiles(self.brand, profiles)

        self.assertEqual(len(findings), 1)
        self.assertGreaterEqual(findings[0]["risk_score"], 30)
        self.assertTrue(findings[0]["reasons"])

    def test_unrelated_account_has_low_risk(self):
        profiles = [{
            "name": "Random Photography",
            "username": "@randomphotography",
            "platform": "Instagram",
            "url": "https://example.com/random"
        }]

        findings = monitor_social_profiles(self.brand, profiles)

        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["risk_level"], "Low")

    def test_missing_name_and_username_are_handled(self):
        profiles = [{
            "name": "",
            "username": "",
            "platform": "Unknown",
            "url": ""
        }]

        findings = monitor_social_profiles(self.brand, profiles)

        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["risk_score"], 0)

    def test_support_word_alone_does_not_make_unrelated_account_high_risk(self):
        profiles = [{
            "name": "Photography Support",
            "username": "@randomphotography_support",
            "platform": "Instagram",
            "url": "https://example.com/random-support"
        }]

        findings = monitor_social_profiles(self.brand, profiles)

        self.assertEqual(len(findings), 1)
        self.assertNotEqual(findings[0]["risk_level"], "High")

    def test_spacing_change_in_brand_name_is_detected(self):
        profiles = [{
            "name": "Nova Bank",
            "username": "@nova_bank",
            "platform": "Instagram",
            "url": "https://example.com/nova_bank"
        }]

        findings = monitor_social_profiles(self.brand, profiles)

        self.assertEqual(len(findings), 1)
        self.assertGreaterEqual(findings[0]["risk_score"], 30)

    def test_added_support_word_with_brand_match_is_flagged(self):
        profiles = [{
            "name": "NovaBank Customer Support",
            "username": "@novabank_customer_support",
            "platform": "Instagram",
            "url": "https://example.com/novabank-support"
        }]

        findings = monitor_social_profiles(self.brand, profiles)

        self.assertEqual(len(findings), 1)
        self.assertGreaterEqual(findings[0]["risk_score"], 30)

    def test_unrelated_support_account_is_not_high_risk(self):
        profiles = [{
            "name": "Garden Support",
            "username": "@garden_help",
            "platform": "Instagram",
            "url": "https://example.com/garden-help"
        }]

        findings = monitor_social_profiles(self.brand, profiles)

        self.assertEqual(len(findings), 1)
        self.assertNotEqual(findings[0]["risk_level"], "High")


if __name__ == "__main__":
    unittest.main()