import unittest

from cloud.rules import DEFAULT_THRESHOLD, display_status, judge, next_event


class AlertRuleTest(unittest.TestCase):
    def test_threshold_matches_original_rule(self):
        self.assertEqual(DEFAULT_THRESHOLD, 80.0)
        self.assertEqual(judge(80), "normal")
        self.assertEqual(judge(80.1), "alert")

    def test_bad_temperature_is_not_an_alert(self):
        self.assertEqual(judge("hot"), "normal")
        self.assertEqual(judge(None), "normal")
        self.assertIsNone(next_event("normal", "hot"))
        self.assertIsNone(next_event("alert", None))

    def test_alert_is_raised_once_until_it_clears(self):
        self.assertEqual(next_event(None, 86)["type"], "raise")
        self.assertIsNone(next_event("alert", 91))
        self.assertEqual(next_event("alert", 70)["type"], "clear")
        self.assertIsNone(next_event("normal", 60))

    def test_offline_uses_report_time_only(self):
        fresh = {"status": "alert", "timestamp": 1000}
        stale = {"status": "normal", "timestamp": 1000}
        self.assertEqual(display_status(fresh, now=1006, interval=2), "alert")
        self.assertEqual(display_status(stale, now=1007, interval=2), "offline")
        self.assertEqual(display_status({"status": "alert"}, now=1007, interval=2), "offline")


if __name__ == "__main__":
    unittest.main()
