"""C4 annual replay, negative controls, and accounting tests."""
from dataclasses import asdict, replace
import gzip
import json
from pathlib import Path
import tempfile
import unittest

from annual_storage import (NO_STORAGE, SCENARIOS, SOC, STORAGE, annual_hours,
                            evaluate_case, summarize, write_trace)
from storage_dispatch import Dispatch, Hour, Plant, evaluate_schedule


class AnnualStorageTests(unittest.TestCase):
    def test_hand_calculated_shift_with_frozen_losses(self):
        hours = (Hour(10, 10, 40), Hour(10, 20, 130))
        reference, selected, rejection = evaluate_case(Plant(STORAGE), hours)
        self.assertIsNone(rejection)
        self.assertEqual(reference.dispatch_cost, 2760)
        self.assertAlmostEqual(selected.dispatch_cost, 2646.828125)
        self.assertEqual(selected.hourly[0].storage.closing_soc, 7)
        self.assertEqual(selected.hourly[1].storage.discharge, 5.359375)
        self.assertEqual(selected.hourly[1].storage.closing_soc, 0)

    def test_all_annual_scenarios_are_feasible_and_cyclic(self):
        plant = Plant(STORAGE)
        for scenario in SCENARIOS:
            with self.subTest(scenario=scenario):
                hours = annual_hours(scenario)
                self.assertEqual(len(hours), 8760)
                reference, selected, _ = evaluate_case(plant, hours)
                for arm in (reference, selected):
                    record = summarize(hours, arm)
                    self.assertEqual(record["terminal_soc_mwh"], SOC)
                    self.assertLessEqual(record["max_soc_mwh"], STORAGE.capacity)
                    self.assertEqual(record["unmet_electricity_mwh"], 0)
                    self.assertLessEqual(record["unmet_heat_mwh"], 1e-9)
                if scenario == "heat_pump_outage_proxy":
                    self.assertTrue(all(not hour.pump_available for hour in hours[:48]))
                    self.assertTrue(all(row.pump_electricity == 0 for row in selected.hourly[:48]))
                    self.assertTrue(hours[48].pump_available)

    def test_annual_negative_controls_have_identical_traces(self):
        hours = annual_hours("baseline")
        plant = Plant(STORAGE)
        variants = (
            (replace(plant, storage=NO_STORAGE), hours),
            (replace(plant, storage=replace(STORAGE, charge_limit=0)), hours),
            (plant, tuple(replace(hour, price=65) for hour in hours)),
            (replace(plant, pump_limit=0), hours),
        )
        for config, inputs in variants:
            with self.subTest(config=config, price=inputs[0].price):
                reference, selected, rejection = evaluate_case(config, inputs)
                self.assertIsNone(rejection)
                self.assertEqual(reference, selected)

    def test_annual_export_round_trips_through_c2(self):
        hours = annual_hours("baseline")
        plant = Plant(STORAGE)
        reference, selected, _ = evaluate_case(plant, hours)
        with tempfile.TemporaryDirectory() as tmp:
            trace = Path(tmp) / "replay.jsonl.gz"
            write_trace(trace, hours, reference, selected)
            with gzip.open(trace, "rt", encoding="utf-8") as stream:
                rows = [json.loads(line) for line in stream]
        self.assertEqual([row["hour"] for row in rows], list(range(8760)))
        replay_inputs = tuple(Hour(**row["input"]) for row in rows)
        for label, config in (("no_storage", replace(plant, storage=NO_STORAGE)),
                              ("equal_resource_control", plant)):
            dispatches = tuple(Dispatch(**row[label]["dispatch"]) for row in rows)
            replayed = evaluate_schedule(config, replay_inputs, dispatches,
                                         initial_soc=SOC, terminal_soc=SOC)
            self.assertEqual([asdict(row) for row in replayed],
                             [row[label]["result"] for row in rows])


if __name__ == "__main__":
    unittest.main()
