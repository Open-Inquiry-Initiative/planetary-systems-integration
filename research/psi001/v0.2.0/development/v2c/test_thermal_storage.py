"""Independent hand calculations for the isolated C1 storage boundary."""
import random
import unittest

from thermal_storage import ABS_TOL, Storage, run_schedule, step


class ThermalStorageTests(unittest.TestCase):
    def assert_conserved(self, record):
        output = (record.closing_soc + record.discharge + record.retention_loss
                  + record.charge_loss + record.discharge_loss)
        self.assertAlmostEqual(record.opening_soc + record.charge, output, delta=ABS_TOL)
        self.assertLessEqual(abs(record.balance_residual), ABS_TOL)

    def test_two_hour_lossless_cycle_hits_capacity_and_rate(self):
        records = run_schedule(Storage(4, 4, 4), [(4, 0), (0, 4)])
        self.assertEqual([r.closing_soc for r in records], [4, 0])
        for r in records:
            self.assertEqual((r.retention_loss, r.charge_loss, r.discharge_loss), (0, 0, 0))
            self.assert_conserved(r)

    def test_three_hour_cycle_conserves_heat_with_all_losses(self):
        storage = Storage(8, 16, 3, charge_efficiency=0.5,
                          discharge_efficiency=0.5, retention=0.75)
        records = run_schedule(storage, [(16, 0), (0, 0), (0, 2.25)])
        expected = [
            (0, 8, 0, 8, 0),
            (8, 6, 2, 0, 0),
            (6, 0, 1.5, 0, 2.25),
        ]
        for r, want in zip(records, expected, strict=True):
            self.assertEqual((r.opening_soc, r.closing_soc, r.retention_loss,
                              r.charge_loss, r.discharge_loss), want)
            self.assert_conserved(r)

    def test_four_hour_zero_capacity_is_a_no_storage_pass_through(self):
        heat_produced = (2, 5, 0, 3)
        records = run_schedule(Storage(0, 10, 10), [(0, 0)] * len(heat_produced))
        delivered = tuple(heat - r.charge + r.discharge
                          for heat, r in zip(heat_produced, records, strict=True))
        self.assertEqual(delivered, heat_produced)
        for r in records:
            self.assertEqual((r.opening_soc, r.closing_soc, r.balance_residual), (0, 0, 0))

    def test_nonzero_initial_soc_is_restored(self):
        records = run_schedule(Storage(4, 2, 2), [(0, 2), (2, 0)], initial_soc=2)
        self.assertEqual([r.closing_soc for r in records], [0, 2])

    def test_terminal_depletion_and_surplus_are_rejected(self):
        storage = Storage(4, 4, 4)
        for schedule, opening in (([(0, 1), (0, 0)], 2), ([(1, 0), (0, 0)], 0)):
            with self.subTest(schedule=schedule), self.assertRaisesRegex(ValueError, "terminal SOC"):
                run_schedule(storage, schedule, initial_soc=opening)

    def test_zero_retention_can_remove_opening_soc_but_not_new_charge(self):
        records = run_schedule(Storage(4, 4, 4, retention=0),
                               [(0, 0), (3, 0)], initial_soc=3)
        self.assertEqual([r.closing_soc for r in records], [0, 3])
        self.assertEqual([r.retention_loss for r in records], [3, 0])
        for record in records:
            self.assert_conserved(record)

    def test_invalid_parameters_are_rejected(self):
        for overrides in (
            {"capacity": -1}, {"charge_limit": True}, {"discharge_limit": float("inf")},
            {"charge_efficiency": 0}, {"discharge_efficiency": 1.01},
            {"discharge_efficiency": float("nan")}, {"retention": -0.1}, {"retention": 1.1},
        ):
            config = {"capacity": 4, "charge_limit": 3, "discharge_limit": 3, **overrides}
            with self.subTest(config=config), self.assertRaises(ValueError):
                Storage(**config)

    def test_invalid_flows_and_states_are_rejected(self):
        storage = Storage(4, 3, 3, retention=0.5)
        for soc, charge, discharge, reason in (
            (-1, 0, 0, "SOC"), (5, 0, 0, "SOC"),
            (0, -1, 0, "charge"), (0, 0, float("nan"), "discharge"),
            (0, True, 0, "charge"), (0, 4, 0, "rate limit"), (4, 0, 4, "rate limit"),
            (0, 1, 1, "simultaneous"), (4, 3, 0, "capacity"),
            (2, 0, 1.5, "available SOC"),
        ):
            with self.subTest(soc=soc, charge=charge, discharge=discharge):
                with self.assertRaisesRegex(ValueError, reason):
                    step(storage, soc, charge=charge, discharge=discharge)
        with self.assertRaisesRegex(ValueError, "zero-capacity"):
            step(Storage(0, 1, 1), 0, charge=1, discharge=0)

    def test_seeded_feasible_transitions_obey_bounds_and_conserve_heat(self):
        rng = random.Random(20261120)
        storage = Storage(10, 4, 3, 0.75, 0.8, 0.9)
        soc = 5
        for hour in range(128):
            retained = soc * 0.9
            if hour % 2 == 0:
                charge = rng.random() * min(4, (10 - retained) / 0.75)
                discharge = 0
            else:
                charge = 0
                discharge = rng.random() * min(3, retained * 0.8)
            r = step(storage, soc, charge=charge, discharge=discharge)
            self.assert_conserved(r)
            self.assertGreaterEqual(r.closing_soc, 0)
            self.assertLessEqual(r.closing_soc, 10)
            self.assertLessEqual(r.charge, 4)
            self.assertLessEqual(r.discharge, 3)
            self.assertEqual(r.charge * r.discharge, 0)
            self.assertGreaterEqual(min(r.retention_loss, r.charge_loss, r.discharge_loss), 0)
            soc = r.closing_soc


if __name__ == "__main__":
    unittest.main()
