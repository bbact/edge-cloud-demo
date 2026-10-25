import unittest

from cloud.rules import THRESHOLD, judge, next_event


class AlertRuleTest(unittest.TestCase):
    def test_threshold_matches_original_rule(self):
        self.assertEqual(THRESHOLD, 80.0)
        self.assertEqual(judge(80), "normal")
        self.assertEqual(judge(80.1), "alert")

    def test_alert_is_raised_once_until_it_clears(self):
        self.assertEqual(next_event(None, 86)["type"], "raise")
        self.assertIsNone(next_event("alert", 91))
        self.assertEqual(next_event("alert", 70)["type"], "clear")
        self.assertIsNone(next_event("normal", 60))


if __name__ == "__main__":
    unittest.main()
