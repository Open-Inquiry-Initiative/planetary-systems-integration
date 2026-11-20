"""Executable V2-A regression fixtures for the hourly input contract."""
import unittest
from unittest.mock import patch

import psi001_annual as model


def shared_price(hour, price):
    return price


def run(electric, heat, prices, *, hours=1, scenario="baseline", tariff=shared_price):
    return model.run(scenario, tariff, electric, heat, prices, expected_hours=hours)


class InputContractTests(unittest.TestCase):
    def test_original_truncation_fixture_is_rejected(self):
        with self.assertRaisesRegex(ValueError, r"heat must contain exactly 2 hours; got 1"):
            run([10, 10], [25], [40, 40], hours=2)

    def test_original_negative_cost_fixture_is_rejected(self):
        with self.assertRaisesRegex(ValueError, r"electric\[0\] must be nonnegative"):
            run([-5], [0], [40])

    def test_default_horizon_rejects_equal_but_short_inputs(self):
        with self.assertRaisesRegex(ValueError, r"exactly 8760 hours; got 1"):
            model.run("baseline", shared_price, [0], [0], [0])

    def test_empty_and_oversized_series_are_rejected(self):
        for series, label in (([], "electric"), ([0, 0], "electric")):
            with self.subTest(series=series):
                with self.assertRaisesRegex(ValueError, rf"{label} must contain exactly 1"):
                    run(series, [0], [0])

    def test_invalid_expected_hours(self):
        for hours in (0, -1, True, 1.0):
            with self.subTest(hours=hours), self.assertRaisesRegex(ValueError, "positive integer"):
                run([0], [0], [0], hours=hours)

    def test_negative_heat_is_rejected(self):
        with self.assertRaisesRegex(ValueError, r"heat\[0\] must be nonnegative"):
            run([0], [-1], [0])

    def test_invalid_hourly_values_are_rejected(self):
        for value in (float("nan"), float("inf"), float("-inf"), True, "5"):
            for series in range(3):
                with self.subTest(value=value, series=series):
                    inputs = [[0], [0], [0]]
                    inputs[series] = [value]
                    with self.assertRaisesRegex(ValueError, "finite number"):
                        run(*inputs)

    def test_invalid_tariff_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "must be callable"):
            run([0], [0], [0], tariff=None)
        with self.assertRaisesRegex(ValueError, r"baseline_tariff\(0\).*finite"):
            run([0], [0], [0], tariff=lambda h, p: float("nan"))

    def test_unknown_scenario_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "unknown scenario"):
            run([0], [0], [0], scenario="misspelled")

    def test_invalid_equipment_constants_are_rejected(self):
        for name, value in (("COP", 0), ("COP", float("inf")), ("BOILER_LIMIT", -1),
                            ("PUMP_LIMIT", -1), ("IMPORT_LIMIT", -1)):
            with self.subTest(name=name, value=value), patch.object(model, name, value):
                with self.assertRaisesRegex(ValueError, name):
                    run([0], [0], [0])

    def test_zero_load_and_zero_capacities_are_valid(self):
        with patch.multiple(model, IMPORT_LIMIT=0, PUMP_LIMIT=0, BOILER_LIMIT=0):
            result = run([0], [0], [0])
        self.assertTrue(result["service_met"])
        self.assertEqual(result["independent"]["dispatch_cost"], 0)

    def test_import_cap_and_negative_price_are_valid(self):
        result = run([95], [0], [-5])
        self.assertTrue(result["service_met"])
        self.assertEqual(result["independent"]["dispatch_cost"], -475)
        self.assertEqual(result["coordinated"]["dispatch_cost"], -475)

    def test_above_capacity_is_reported_as_unmet_demand(self):
        result = run([100], [130], [130])
        self.assertFalse(result["service_met"])
        for planner in ("independent", "coordinated"):
            self.assertEqual(result[planner]["unserved_electric_mwh"], 5)
            self.assertEqual(result[planner]["unserved_heat_mwh"], 30)


if __name__ == "__main__":
    unittest.main()
