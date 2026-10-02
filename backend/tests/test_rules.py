import unittest
from app.services.risk_engine import analyze_rules
from app.services.language_service import translate_analysis_findings, SUPPORTED_LANGUAGES

class TestTrustLensRules(unittest.TestCase):
    
    def test_rule_1_guaranteed_return(self):
        text = "Invest ₹10,000 and get 100% profit with guaranteed 25% monthly return."
        res = analyze_rules(text)
        rule_ids = [f["rule_id"] for f in res["red_flags"]]
        self.assertIn("RF01", rule_ids)
        self.assertGreaterEqual(res["score"], 25)

    def test_rule_2_urgency(self):
        text = "Offer valid only today! Act now, only 5 slots left before offer expires."
        res = analyze_rules(text)
        rule_ids = [f["rule_id"] for f in res["red_flags"]]
        self.assertIn("RF02", rule_ids)

    def test_rule_3_insider_claim(self):
        text = "Exclusive operator news! My source inside the company leaked this secret tip."
        res = analyze_rules(text)
        rule_ids = [f["rule_id"] for f in res["red_flags"]]
        self.assertIn("RF03", rule_ids)

    def test_rule_4_private_group(self):
        text = "Join our exclusive Telegram group now. DM for entry into private VIP channel."
        res = analyze_rules(text)
        rule_ids = [f["rule_id"] for f in res["red_flags"]]
        self.assertIn("RF04", rule_ids)

    def test_rule_5_apk_remote_access(self):
        text = "Download an APK from this link and install AnyDesk for trading support."
        res = analyze_rules(text)
        rule_ids = [f["rule_id"] for f in res["red_flags"]]
        self.assertIn("RF05", rule_ids)

    def test_rule_6_credential_otp(self):
        text = "Share your OTP and enter your UPI PIN to claim your investment bonus."
        res = analyze_rules(text)
        rule_ids = [f["rule_id"] for f in res["red_flags"]]
        self.assertIn("RF06", rule_ids)

    def test_rule_7_shortened_link(self):
        text = "Check our portal at http://bit.ly/sebi-support-example and https://rbi-verification-example.com"
        res = analyze_rules(text)
        rule_ids = [f["rule_id"] for f in res["red_flags"]]
        self.assertIn("RF07", rule_ids)

    def test_rule_8_sebi_claim(self):
        text = "We are a SEBI registered investment opportunity. SEBI Reg No: INA000012345."
        res = analyze_rules(text)
        rule_ids = [f["rule_id"] for f in res["red_flags"]]
        self.assertIn("RF08", rule_ids)
        # Check claim status
        claims = [c for c in res["claims"] if "SEBI" in c["claim"]]
        self.assertTrue(len(claims) > 0)
        self.assertEqual(claims[0]["status"], "VERIFY ON OFFICIAL SOURCE")

    def test_rule_9_specific_trading_tip(self):
        text = "Buy XYZ at ₹500, target ₹650, stop loss ₹450. Jackpot call."
        res = analyze_rules(text)
        rule_ids = [f["rule_id"] for f in res["red_flags"]]
        self.assertIn("RF09", rule_ids)

    def test_rule_10_personal_upi(self):
        text = "Send payment to trader99@okhdfcbank or transfer ₹5,000 to my UPI ID."
        res = analyze_rules(text)
        rule_ids = [f["rule_id"] for f in res["red_flags"]]
        self.assertIn("RF10", rule_ids)

    def test_combination_message(self):
        """
        User requirement:
        "SEBI approved VIP stock tip. Buy at ₹500, target ₹700, stop loss ₹450. Pay ₹5,000 to join our Telegram group."
        Expected multiple flags:
        - SEBI registration/approval claim (RF08)
        - VIP/private group (RF04)
        - Specific trading tip (RF09)
        - Payment request (RF10)
        """
        text = "SEBI approved VIP stock tip. Buy at ₹500, target ₹700, stop loss ₹450. Pay ₹5,000 to join our Telegram group."
        res = analyze_rules(text)
        rule_ids = set(f["rule_id"] for f in res["red_flags"])
        self.assertIn("RF08", rule_ids)
        self.assertIn("RF04", rule_ids)
        self.assertIn("RF09", rule_ids)
        self.assertIn("RF10", rule_ids)
        self.assertEqual(res["risk_level"], "HIGH RISK")

    def test_false_positive_control_otp(self):
        """
        User requirement:
        'Learn what OTP means in financial security.' should NOT automatically trigger RF06
        """
        text = "Learn what OTP means in financial security and cyber protection."
        res = analyze_rules(text)
        rule_ids = [f["rule_id"] for f in res["red_flags"]]
        self.assertNotIn("RF06", rule_ids)

    def test_false_positive_control_sebi(self):
        """
        User requirement:
        'SEBI provides investor education.' should NOT automatically trigger RF08
        """
        text = "SEBI provides investor education and regulatory oversight for the markets."
        res = analyze_rules(text)
        rule_ids = [f["rule_id"] for f in res["red_flags"]]
        self.assertNotIn("RF08", rule_ids)

    def test_multilingual_translation(self):
        text = "URGENT!!! SEBI approved investment. Guaranteed 25% monthly returns. Pay ₹5,000 to activate."
        res = analyze_rules(text)
        
        # Test Gujarati
        res_gu = translate_analysis_findings(res, "gu")
        self.assertEqual(res_gu["language"], "gu")
        self.assertIn("ગુજરાતી", res_gu["language_name"])
        self.assertTrue(any("ગેરંટીડ" in f["title"] for f in res_gu["red_flags"]))
        
        # Test Tamil
        res_ta = translate_analysis_findings(res, "ta")
        self.assertEqual(res_ta["language"], "ta")
        self.assertIn("தமிழ்", res_ta["language_name"])
        self.assertTrue(any("உத்தரவாதமளிக்கப்பட்ட" in f["title"] for f in res_ta["red_flags"]))

        # Verify underlying risk score did not change
        self.assertEqual(res_gu["score"], res["score"])
        self.assertEqual(res_ta["score"], res["score"])

    def test_all_22_scheduled_languages_count(self):
        self.assertEqual(len(SUPPORTED_LANGUAGES), 23) # 22 scheduled + English

if __name__ == "__main__":
    unittest.main()
