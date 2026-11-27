import unittest
from unittest.mock import patch

from collector.events.detector import ProductionEventDetector


class DetectorTests(unittest.TestCase):
    def test_one_event_per_cycle(self):
        detector = ProductionEventDetector("Output", True, 0, "Result")
        self.assertIsNone(detector.update({"Output": False}))
        self.assertIsNotNone(detector.update({"Output": True, "Result": True}))
        self.assertIsNone(detector.update({"Output": True}))
        self.assertIsNone(detector.update({"Output": False}))
        self.assertIsNotNone(detector.update({"Output": True, "Result": False}))

    def test_active_low(self):
        detector = ProductionEventDetector("Output", False, 0)
        self.assertIsNone(detector.update({"Output": True}))
        self.assertIsNotNone(detector.update({"Output": False}))

    def test_numeric_result_waits_for_zero_then_captures_pass_or_fail_once(self):
        detector = ProductionEventDetector(
            "Result_MW3112",
            debounce_ms=0,
            active_values=[1, 2],
            rearm_value=0,
            result_mapping={"1": "PASS", "2": "FAIL"},
        )
        self.assertIsNone(detector.update({"Result_MW3112": 1}))
        self.assertIsNone(detector.update({"Result_MW3112": 0}))
        passed = detector.update({"Result_MW3112": 1, "Coil_Short_MW3008": 12})
        self.assertEqual(passed["result_status"], "PASS")
        self.assertEqual(passed["payload"]["Coil_Short_MW3008"], 12)
        self.assertIsNone(detector.update({"Result_MW3112": 1}))
        self.assertIsNone(detector.update({"Result_MW3112": 2}))
        self.assertIsNone(detector.update({"Result_MW3112": 0}))
        failed = detector.update({"Result_MW3112": 2})
        self.assertEqual(failed["result_status"], "FAIL")

    def test_numeric_result_debounce(self):
        detector = ProductionEventDetector(
            "Result", debounce_ms=100, active_values=[1, 2], rearm_value=0,
            result_mapping={"1": "PASS", "2": "FAIL"},
        )
        detector.update({"Result": 0})
        with patch("collector.events.detector.time.monotonic", side_effect=[10.0, 10.05, 10.11]):
            self.assertIsNone(detector.update({"Result": 1}))
            self.assertIsNone(detector.update({"Result": 1}))
            event = detector.update({"Result": 1})
        self.assertEqual(event["result_status"], "PASS")
