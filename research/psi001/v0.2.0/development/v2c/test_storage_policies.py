"""Hand-worked fixtures for the common V2-C3 scheduling policy."""
import unittest

from storage_dispatch import Dispatch, Hour, Plant
from storage_policies import compare_controls, select_schedule
from thermal_storage import ABS_TOL, Storage


HOURS = (Hour(10, 10, 40), Hour(10, 20, 130))
NO_SHIFT = (Dispatch(4, 0), Dispatch(0, 20))
SHIFT = (Dispatch(8, 0, charge=10), Dispatch(0, 10, discharge=10))


class SchedulingControlsTests(unittest.TestCase):
    def test_equal_information_and_active_storage_in_both_arms(self):
        plant = Plant(Storage(10, 10, 10))
        reference = select_schedule(plant, HOURS, [NO_SHIFT], initial_soc=0, terminal_soc=0)
        self.assertEqual(reference.dispatch_cost, 2760)  # 14*40 + 10*130 + 20*45
        result = compare_controls(plant, iter(HOURS), iter((NO_SHIFT, SHIFT)),
                                  initial_soc=0, terminal_soc=0)
        self.assertFalse(result.coordination_identifiable)
        self.assertEqual(result.independent, result.coordinated_control)
        selection = result.independent
        self.assertEqual((selection.candidate_index, selection.schedule), (1, SHIFT))
        self.assertEqual(selection.dispatch_cost, 2470)  # 18*40 + 10*130 + 10*45
        self.assertEqual((selection.unmet_electricity, selection.unmet_heat), (0, 0))
        self.assertEqual([r.storage.closing_soc for r in selection.hourly], [10, 0])
        for hour, row in zip(HOURS, selection.hourly, strict=True):
            self.assertAlmostEqual(row.electricity_purchased, hour.electric_load
                                   + row.pump_electricity, delta=ABS_TOL)
            losses = row.storage.retention_loss + row.storage.charge_loss + row.storage.discharge_loss
            self.assertAlmostEqual(row.heat_produced + row.storage.opening_soc,
                                   row.heat_delivered + row.storage.closing_soc + losses,
                                   delta=ABS_TOL)

    def test_zero_capacity_rejects_shift_for_both_arms(self):
        result = compare_controls(Plant(Storage(0, 0, 0)), HOURS, (SHIFT, NO_SHIFT),
                                  initial_soc=0, terminal_soc=0)
        self.assertEqual(result.independent, result.coordinated_control)
        self.assertEqual(result.independent.schedule, NO_SHIFT)
        self.assertEqual(result.independent.dispatch_cost, 2760)

    def test_noncyclic_and_import_cap_candidates_are_ineligible(self):
        plant = Plant(Storage(10, 10, 10))
        hours = (Hour(95, 0, 0), Hour(0, 0, 0))
        idle = (Dispatch(0, 0), Dispatch(0, 0))
        noncyclic = (Dispatch(0, 1, charge=1), Dispatch(0, 0))
        over_import = (Dispatch(1, 0, charge=2.5), Dispatch(0, 0))
        result = select_schedule(plant, hours, (noncyclic, over_import, idle),
                                 initial_soc=0, terminal_soc=0)
        self.assertEqual(result.candidate_index, 2)
        self.assertEqual(result.hourly[0].electricity_purchased, 95)
        self.assertEqual(result.hourly[-1].storage.closing_soc, 0)
        with self.assertRaisesRegex(ValueError, "no feasible"):
            select_schedule(plant, hours, (noncyclic, over_import), initial_soc=0, terminal_soc=0)

    def test_service_priority_and_stable_tie_break(self):
        plant = Plant(Storage(0, 0, 0))
        hours = (Hour(0, 5, 112.5), Hour(1, 0, 10))
        shortfall = (Dispatch(0, 0), Dispatch(0, 0))
        boiler = (Dispatch(0, 5), Dispatch(0, 0))
        pump = (Dispatch(2, 0), Dispatch(0, 0))
        result = select_schedule(plant, hours, (shortfall, boiler, pump),
                                 initial_soc=0, terminal_soc=0)
        self.assertEqual(result.schedule, boiler)
        self.assertEqual((result.dispatch_cost, result.unmet_heat), (235, 0))
        reversed_tie = select_schedule(plant, hours, (shortfall, pump, boiler),
                                       initial_soc=0, terminal_soc=0)
        self.assertEqual(reversed_tie.schedule, pump)


if __name__ == "__main__":
    unittest.main()
