import unittest
from decimal import Decimal
from v3a_independent_audit import audit_all, audit_row


class IndependentAuditTests(unittest.TestCase):
    def test_all_six_expected_rows(self):
        rows = audit_all()
        self.assertEqual(len(rows), 6)
        for index, row in enumerate(rows):
            accept = index < 3
            self.assertEqual(row["accepted"], accept)
            self.assertEqual(Decimal(row["cost"]), Decimal("37.5") if accept else Decimal("600"))
            self.assertEqual(Decimal(row["gross_gap"]), Decimal("0") if accept else Decimal("562.5"))
            self.assertEqual(Decimal(row["central_cost"]), Decimal("37.5"))
            self.assertEqual(row["logical_messages"], 2)

    def test_tie_boundary(self):
        self.assertFalse(audit_row("75")["accepted"])
        self.assertTrue(audit_row("74.99")["accepted"])

    def test_invalid_prices(self):
        for price in ("-1", "NaN", "Infinity"):
            with self.assertRaises(ValueError):
                audit_row(price)


if __name__ == "__main__":
    unittest.main()
