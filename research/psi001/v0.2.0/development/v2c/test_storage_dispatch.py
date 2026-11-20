"""Hand-calculated C2 plant and storage integration fixtures."""
from pathlib import Path
import runpy
import unittest

from storage_dispatch import Dispatch, Hour, Plant, evaluate_hour, evaluate_schedule
from thermal_storage import ABS_TOL, Storage


class StorageDispatchTests(unittest.TestCase):
    def assert_balances(self, hour, row):
        storage = row.storage
        self.assertAlmostEqual(
            row.electricity_purchased + row.unmet_electricity,
            hour.electric_load + row.pump_electricity, delta=ABS_TOL)
        self.assertAlmostEqual(row.heat_delivered + row.unmet_heat, hour.heat_load, delta=ABS_TOL)
        self.assertAlmostEqual(
            row.heat_produced + storage.opening_soc,
            row.heat_delivered + storage.closing_soc + storage.retention_loss
            + storage.charge_loss + storage.discharge_loss, delta=ABS_TOL)
        for residual in (row.electricity_balance_residual, row.heat_balance_residual,
                         storage.balance_residual):
            self.assertLessEqual(abs(residual), ABS_TOL)

    def test_two_hour_shift_accounts_for_cop_heat_and_realized_prices(self):
        plant = Plant(Storage(10, 10, 10))
        hours = (Hour(10, 10, 40), Hour(10, 20, 130))
        rows = evaluate_schedule(plant, hours, (Dispatch(8, 0, charge=10),
                                                Dispatch(0, 10, discharge=10)),
                                 initial_soc=0, terminal_soc=0)
        self.assertEqual([r.pump_heat for r in rows], [20, 0])
        self.assertEqual([r.boiler_heat for r in rows], [0, 10])
        self.assertEqual([r.heat_produced for r in rows], [20, 10])
        self.assertEqual([r.heat_delivered for r in rows], [10, 20])
        self.assertEqual([r.storage.closing_soc for r in rows], [10, 0])
        self.assertEqual([r.electricity_purchased for r in rows], [18, 10])
        self.assertEqual([r.electricity_cost for r in rows], [720, 1300])
        self.assertEqual([r.boiler_cost for r in rows], [0, 450])
        self.assertEqual([r.realized_cost for r in rows], [720, 1750])
        for hour, row in zip(hours, rows, strict=True):
            self.assert_balances(hour, row)

    def test_three_hour_lossy_cycle_and_outages_have_no_backup(self):
        storage = Storage(8, 16, 3, charge_efficiency=0.5,
                          discharge_efficiency=0.5, retention=0.75)
        hours = (Hour(10, 4, 40), Hour(2, 1, 50, grid_available=False,
                                     boiler_available=False, storage_available=False),
                 Hour(10, 3, 130, pump_available=False, boiler_available=False))
        rows = evaluate_schedule(Plant(storage), hours,
                                 (Dispatch(8, 0, charge=16), Dispatch(0, 0),
                                  Dispatch(0, 0, discharge=2.25)),
                                 initial_soc=0, terminal_soc=0)
        self.assertEqual([r.storage.closing_soc for r in rows], [8, 6, 0])
        self.assertEqual([r.storage.retention_loss for r in rows], [0, 2, 1.5])
        self.assertEqual([r.storage.charge_loss for r in rows], [8, 0, 0])
        self.assertEqual([r.storage.discharge_loss for r in rows], [0, 0, 2.25])
        self.assertEqual([r.heat_delivered for r in rows], [4, 0, 2.25])
        self.assertEqual([r.unmet_heat for r in rows], [0, 1, 0.75])
        self.assertEqual([r.unmet_electricity for r in rows], [0, 2, 0])
        self.assertEqual([r.electricity_purchased for r in rows], [18, 0, 10])
        self.assertEqual([r.realized_cost for r in rows], [720, 0, 1300])
        for hour, row in zip(hours, rows, strict=True):
            self.assert_balances(hour, row)

    def test_four_hour_zero_storage_matches_hand_totals_and_v2a(self):
        hours = (Hour(90, 20, 40), Hour(10, 25, 130),
                 Hour(100, 130, 130), Hour(0, 0, -10))
        dispatches = (Dispatch(5, 7.5), Dispatch(0, 25), Dispatch(0, 100), Dispatch(0, 0))
        rows = evaluate_schedule(Plant(Storage(0, 0, 0)), hours, dispatches,
                                 initial_soc=0, terminal_soc=0)
        self.assertEqual([r.realized_cost for r in rows], [4137.5, 2425, 16850, 0])
        v2a = runpy.run_path(str(Path(__file__).resolve().parents[1] / "psi001_annual.py"))
        reference = v2a["run"]("baseline", lambda h, price: price,
                               [h.electric_load for h in hours], [h.heat_load for h in hours],
                               [h.price for h in hours], expected_hours=4)
        for arm in reference["independent"], reference["coordinated"]:
            for old, new in (("dispatch_cost", "realized_cost"),
                             ("pump_electric_mwh", "pump_electricity"),
                             ("unserved_electric_mwh", "unmet_electricity"),
                             ("unserved_heat_mwh", "unmet_heat")):
                self.assertEqual(arm[old], sum(getattr(r, new) for r in rows))
        for hour, row in zip(hours, rows, strict=True):
            self.assert_balances(hour, row)

    def test_negative_prices_score_only_actual_purchases(self):
        row = evaluate_hour(Plant(Storage(0, 0, 0)), Hour(2, 5, -10), Dispatch(2, 0), 0)
        self.assertEqual((row.electricity_purchased, row.realized_cost), (4, -40))

    def test_explicit_cyclic_targets_and_schedule_lengths_are_enforced(self):
        plant = Plant(Storage(2, 2, 2))
        hours = (Hour(0, 1, 0), Hour(0, 0, 0))
        flows = (Dispatch(0, 0, discharge=1), Dispatch(0, 1, charge=1))
        rows = evaluate_schedule(plant, hours, flows, initial_soc=1, terminal_soc=1)
        self.assertEqual([r.storage.closing_soc for r in rows], [0, 1])
        with self.assertRaisesRegex(ValueError, "identical"):
            evaluate_schedule(plant, hours, flows, initial_soc=1, terminal_soc=0)
        with self.assertRaisesRegex(ValueError, "terminal target"):
            evaluate_schedule(plant, hours, (flows[0], Dispatch(0, 0)),
                              initial_soc=1, terminal_soc=1)
        for bad_hours, bad_flows in ((hours[:1], flows), (hours, flows[:1]), ((), ())):
            with self.subTest(hours=bad_hours, flows=bad_flows), self.assertRaises(ValueError):
                evaluate_schedule(plant, bad_hours, bad_flows, initial_soc=1, terminal_soc=1)

    def test_invalid_dispatches_cannot_bypass_constraints(self):
        plant = Plant(Storage(4, 2, 2))
        for hour, dispatch, error in (
            (Hour(94, 10, 0), Dispatch(2, 0), "import capacity"),
            (Hour(0, 100, 0), Dispatch(19, 0), "pump or import capacity"),
            (Hour(0, 10, 0, pump_available=False), Dispatch(1, 0), "pump"),
            (Hour(0, 10, 0, grid_available=False), Dispatch(1, 0), "import"),
            (Hour(0, 120, 0), Dispatch(0, 101), "boiler"),
            (Hour(0, 10, 0, boiler_available=False), Dispatch(0, 1), "boiler"),
            (Hour(0, 1, 0, storage_available=False), Dispatch(0, 1, charge=1), "unavailable"),
            (Hour(0, 1, 0), Dispatch(0, 0, charge=1), "exceeds heat production"),
            (Hour(0, 1, 0), Dispatch(0, 2), "dumping"),
            (Hour(0, 0, 0), Dispatch(0, 1, charge=1, discharge=1), "simultaneous"),
            (Hour(0, 0, 0), Dispatch(0, 3, charge=3), "rate limit"),
            (Hour(0, 1, 0), Dispatch(0, 0, discharge=1), "available SOC"),
        ):
            with self.subTest(hour=hour, dispatch=dispatch), self.assertRaisesRegex(ValueError, error):
                evaluate_hour(plant, hour, dispatch, 0)
        with self.assertRaisesRegex(ValueError, "zero-capacity"):
            evaluate_hour(Plant(Storage(0, 1, 1)), Hour(0, 0, 0), Dispatch(0, 1, charge=1), 0)

    def test_nonfinite_and_negative_inputs_are_rejected(self):
        for invalid in (
            lambda: Hour(-1, 0, 0), lambda: Hour(0, -1, 0),
            lambda: Hour(0, 0, float("inf")), lambda: Hour(0, 0, 0, grid_available=1),
            lambda: Dispatch(-1, 0), lambda: Dispatch(0, float("nan")),
            lambda: Plant(Storage(0, 0, 0), cop=0),
            lambda: Plant(Storage(0, 0, 0), import_limit=-1),
            lambda: evaluate_hour(Plant(Storage(0, 0, 0)), Hour(95, 0, 1e308), Dispatch(0, 0), 0),
        ):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                invalid()


if __name__ == "__main__":
    unittest.main()
