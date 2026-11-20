import unittest
from v3a_fixture import Fixture
from v3a_bounded_protocol import bilateral_one_round, compare_price, sweep


class TestV3A5(unittest.TestCase):
    def test_preregistered_sweep(self):
        rows = sweep()
        self.assertEqual([r["price"] for r in rows], [0, 40, 74.99, 75, 80, 100])
        for row in rows:
            accepted = row["price"] < 75
            self.assertEqual(row["bilateral"]["messages"][1].kind, "accept" if accepted else "reject")
            self.assertEqual(row["bilateral"]["message_count"], 2)
            self.assertAlmostEqual(row["bilateral"]["dispatch"]["cost"], 37.5 if accepted else 600)
            self.assertAlmostEqual(row["gross_protocol_gap"], 0 if accepted else 562.5)
            self.assertAlmostEqual(row["central"]["cost"], 37.5)

    def test_message_accounting(self):
        r = bilateral_one_round(40)
        self.assertEqual([(m.sender, m.recipient) for m in r["messages"]], [("A", "B"), ("B", "A")])
        self.assertAlmostEqual(r["internal_payment"], 300)
        self.assertAlmostEqual(r["dispatch"]["cost"], 37.5)

    def test_tie_rejects(self):
        self.assertEqual(bilateral_one_round(75)["messages"][1].kind, "reject")

    def test_zero_link(self):
        f = Fixture(link_capacity_mwh=0)
        self.assertAlmostEqual(compare_price(80, f)["gross_protocol_gap"], 0)

    def test_invalid_prices(self):
        for p in (-1, float("nan"), float("inf")):
            with self.assertRaises(ValueError):
                bilateral_one_round(p)


if __name__ == "__main__":
    unittest.main()
