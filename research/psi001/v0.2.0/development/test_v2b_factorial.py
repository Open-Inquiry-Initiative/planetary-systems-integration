"""Hand-calculated coverage for the preregistered V2-B contrasts."""
import unittest

import v2b_factorial as harness


class FactorialControlTests(unittest.TestCase):
    def assert_row_invariants(self, result):
        for row in result["cells"].values():
            independent = row["independent"]
            coordinated = row["coordinated_control"]
            for field in ("dispatch_cost", "pump_electric_mwh",
                          "unserved_electric_mwh", "unserved_heat_mwh"):
                self.assertEqual(independent[field], coordinated[field])
            self.assertEqual(independent["overhead"], 0)
            self.assertEqual(coordinated["overhead"], 100_000)
            for cell in row.values():
                self.assertEqual(cell["total_cost"], cell["dispatch_cost"] + cell["overhead"])

    def test_no_flexibility_equivalence_at_import_ceiling(self):
        result = harness.compare("baseline", [95], [25], [130], expected_hours=1)
        self.assert_row_invariants(result)
        for row in result["cells"].values():
            a = row["independent"]
            self.assertEqual(a["dispatch_cost"], 13_475)  # 95*130 + 25*45
            self.assertEqual(a["pump_electric_mwh"], 0)
            self.assertEqual(a["unserved_heat_mwh"], 0)
            self.assertEqual(a["unserved_electric_mwh"], 0)
        self.assertEqual(result["savings_without_overhead"], dict.fromkeys(
            ("information_only", "coordination_only", "interaction", "combined"), 0))
        self.assertEqual(result["savings_with_overhead"]["combined"], -100_000)

    def test_flexible_hour_uses_same_decision_rule_within_each_row(self):
        result = harness.compare("baseline", [10], [25], [130], expected_hours=1)
        self.assert_row_invariants(result)
        limited = result["cells"]["limited"]["independent"]
        shared = result["cells"]["shared_hourly"]["independent"]
        self.assertEqual((limited["pump_electric_mwh"], limited["dispatch_cost"]), (10, 2600))
        self.assertEqual((shared["pump_electric_mwh"], shared["dispatch_cost"]), (0, 2425))
        self.assertEqual(result["savings_without_overhead"], {
            "information_only": 175, "coordination_only": 0, "interaction": 0, "combined": 175,
        })
        self.assertEqual(result["savings_with_overhead"], {
            "information_only": 175, "coordination_only": -100_000,
            "interaction": 0, "combined": -99_825,
        })

    def test_identical_prices_make_information_arms_equivalent(self):
        result = harness.compare("baseline", [10, 5], [25, 15], [65, 65], expected_hours=2)
        self.assert_row_invariants(result)
        self.assertEqual(result["cells"]["limited"], result["cells"]["shared_hourly"])
        self.assertEqual(result["cells"]["shared_hourly"]["independent"]["pump_electric_mwh"], 16)

    def test_contrasts_recover_nonzero_interaction_from_independent_fixture(self):
        cells = {
            "limited": {"independent": {"cost": 100}, "coordinated_control": {"cost": 98}},
            "shared_hourly": {"independent": {"cost": 90}, "coordinated_control": {"cost": 80}},
        }
        self.assertEqual(harness.cost_contrasts(cells, "cost"), {
            "information_only": 10, "coordination_only": 2, "interaction": 8, "combined": 20,
        })

    def test_accounting_does_not_mistake_unserved_demand_for_equivalence_to_zero(self):
        result = harness.compare("baseline", [100], [130], [130], expected_hours=1)
        self.assert_row_invariants(result)
        for row in result["cells"].values():
            for cell in row.values():
                self.assertEqual(cell["unserved_electric_mwh"], 5)
                self.assertEqual(cell["unserved_heat_mwh"], 30)


if __name__ == "__main__":
    unittest.main()
