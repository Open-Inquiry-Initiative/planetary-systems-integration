import unittest
from v3a_instrumentation import wire_bytes, bilateral_wire, coordinator_wire, comparison, timed_sample


class InstrumentationTests(unittest.TestCase):
    def test_utf8_wire_determinism(self):
        a = {"b": 2, "a": "é"}
        self.assertEqual(wire_bytes(a), wire_bytes({"a": "é", "b": 2}))
        self.assertGreater(wire_bytes(a), 0)

    def test_two_messages_per_protocol(self):
        for result in (bilateral_wire(40), coordinator_wire()):
            self.assertEqual(result["message_count"], 2)
            self.assertEqual(len(result["messages"]), 2)
            self.assertEqual(result["payload_bytes"], sum(map(wire_bytes, result["messages"])))

    def test_costs_unchanged(self):
        self.assertEqual(comparison(40)["gross_operating_gap"], 0)
        self.assertEqual(comparison(80)["gross_operating_gap"], 562.5)

    def test_timing_measurement_has_no_synthetic_latency(self):
        r = timed_sample(lambda: None, 2)
        self.assertEqual(r["iterations"], 2)
        self.assertGreaterEqual(r["total_ns"], 0)

    def test_invalid_iterations(self):
        with self.assertRaises(ValueError):
            timed_sample(lambda: None, 0)


if __name__ == "__main__":
    unittest.main()
