import unittest
from v3a_common_observation import snapshot, observe, compare
from v3a_fixture import Fixture


class CommonObservationTests(unittest.TestCase):
    def test_same_snapshot(self):
        self.assertEqual(observe("bilateral")["message"]["data"],
                         observe("coordinator")["message"]["data"])
        self.assertEqual(len(snapshot()), 6)

    def test_account_every_message(self):
        r = compare()
        self.assertEqual(r["bilateral"]["total_messages"], 3)
        self.assertEqual(r["coordinator"]["total_messages"], 3)
        self.assertGreater(r["common_snapshot_payload_bytes_each"], 0)
        for policy in ("bilateral", "coordinator"):
            self.assertGreater(r[policy]["observation_envelope_bytes"], 0)
            self.assertGreater(r[policy]["decision_payload_bytes"], 0)

    def test_zero_gap_control(self):
        self.assertEqual(compare(40)["gross_operating_gap"], 0)

    def test_failure_control(self):
        self.assertEqual(compare(80)["gross_operating_gap"], 562.5)

    def test_invalid_policy(self):
        with self.assertRaises(ValueError):
            observe("unregistered")

    def test_zero_link_snapshot(self):
        r = compare(80, Fixture(link_capacity_mwh=0))
        self.assertEqual(r["gross_operating_gap"], 0)


if __name__ == "__main__":
    unittest.main()
