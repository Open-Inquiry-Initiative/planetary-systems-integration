"""Fixed-menu annual PSI-001 replay. Run with a new output directory."""
import argparse
from dataclasses import asdict, replace
import gzip
import hashlib
import json
import math
from pathlib import Path
import platform
import runpy
import sys

from storage_dispatch import Dispatch, Hour, Plant, evaluate_schedule
from storage_policies import compare_controls, select_schedule
from thermal_storage import ABS_TOL, Storage


NO_STORAGE = Storage(0, 0, 0)
STORAGE = Storage(16, 8, 8, 0.875, 0.875, 0.875)
SOC = 0
OVERHEAD = 100_000
SCENARIOS = ("baseline", "cold_snap", "heat_pump_outage_proxy")


def annual_hours(scenario):
    if scenario not in SCENARIOS:
        raise ValueError(f"unknown annual scenario: {scenario}")
    baseline = runpy.run_path(str(Path(__file__).resolve().parents[1] / "psi001_annual.py"))
    electric, heat, prices = baseline["inputs"]()
    return tuple(Hour(load, demand * 1.30 if scenario == "cold_snap" and index < 72 else demand,
                      price, pump_available=scenario != "heat_pump_outage_proxy" or index >= 48)
                 for index, (load, demand, price) in enumerate(zip(electric, heat, prices, strict=True)))


def spare_pump(plant, hour):
    if not hour.grid_available or not hour.pump_available:
        return 0
    return min(plant.pump_limit, max(0, plant.import_limit - hour.electric_load))


def make_dispatch(plant, hour, pump, boiler, *, charge=0, discharge=0):
    supplied = pump * plant.cop + boiler - charge + discharge
    boiler_limit = plant.boiler_limit if hour.boiler_available else 0
    if 0 < hour.heat_load - supplied <= 1e-12 and boiler < boiler_limit:
        boiler += min(1e-12, boiler_limit - boiler)
    return Dispatch(pump, boiler, charge, discharge)


def no_shift(plant, hour):
    max_pump = min(spare_pump(plant, hour), hour.heat_load / plant.cop)
    boiler_limit = plant.boiler_limit if hour.boiler_available else 0
    pump = max_pump
    if hour.price >= plant.boiler_cost * plant.cop:
        pump = min(max_pump, max(0, hour.heat_load - boiler_limit) / plant.cop)
    boiler = min(boiler_limit, max(0, hour.heat_load - pump * plant.cop))
    return make_dispatch(plant, hour, pump, boiler)


def adjacent_shift(plant, hours, reference):
    schedule = list(reference)
    tank = plant.storage
    useful_per_charge = tank.charge_efficiency * tank.retention * tank.discharge_efficiency
    if not useful_per_charge:
        return tuple(schedule)
    for i in range(0, len(hours) - 1, 2):
        first, second = hours[i:i + 2]
        if not (first.storage_available and second.storage_available):
            continue
        if first.price / plant.cop >= plant.boiler_cost * useful_per_charge:
            continue
        a, b = reference[i:i + 2]
        # Whole-MWh charges and the frozen dyadic efficiencies close each pair exactly.
        charge = math.floor(min((spare_pump(plant, first) - a.pump_electricity) * plant.cop,
                               tank.charge_limit, tank.capacity / tank.charge_efficiency,
                               tank.discharge_limit / useful_per_charge,
                               b.boiler_heat / useful_per_charge))
        if charge <= 0:
            continue
        discharge = charge * useful_per_charge
        schedule[i] = make_dispatch(plant, first, a.pump_electricity + charge / plant.cop,
                                    a.boiler_heat, charge=charge)
        schedule[i + 1] = make_dispatch(plant, second, b.pump_electricity,
                                        b.boiler_heat - discharge, discharge=discharge)
    return tuple(schedule)


def audit(hours, rows):
    maxima = dict(electricity=0.0, heat=0.0, storage=0.0, total_thermal=0.0)
    for hour, row in zip(hours, rows, strict=True):
        storage = row.storage
        residuals = {
            "electricity": math.fsum((row.electricity_purchased, row.unmet_electricity,
                                      -hour.electric_load, -row.pump_electricity)),
            "heat": row.heat_balance_residual,
            "storage": storage.balance_residual,
            "total_thermal": math.fsum((row.heat_produced, storage.opening_soc,
                                        -row.heat_delivered, -storage.closing_soc,
                                        -storage.retention_loss, -storage.charge_loss,
                                        -storage.discharge_loss)),
        }
        for name, residual in residuals.items():
            if not math.isfinite(residual) or abs(residual) > ABS_TOL:
                raise ArithmeticError(f"{name} conservation failed: {residual}")
            maxima[name] = max(maxima[name], abs(residual))
    return maxima


def evaluate_case(plant, hours):
    reference_schedule = tuple(no_shift(plant, hour) for hour in hours)
    reference = select_schedule(replace(plant, storage=NO_STORAGE), hours, (reference_schedule,),
                                initial_soc=SOC, terminal_soc=SOC)
    candidate = adjacent_shift(plant, hours, reference_schedule)
    rejection = None
    try:
        evaluate_schedule(plant, hours, candidate, initial_soc=SOC, terminal_soc=SOC)
    except ValueError as error:
        rejection = str(error)
    menu = (reference_schedule, candidate) if rejection is None else (reference_schedule,)
    controls = compare_controls(plant, hours, menu, initial_soc=SOC, terminal_soc=SOC)
    if controls.coordination_identifiable or controls.independent != controls.coordinated_control:
        raise ArithmeticError("equal-resource negative control diverged")
    return reference, controls.independent, rejection


def summarize(hours, selected):
    rows = selected.hourly
    storage = [row.storage for row in rows]
    return {
        "candidate_index": selected.candidate_index,
        "dispatch_cost": selected.dispatch_cost,
        "unmet_electricity_mwh": selected.unmet_electricity,
        "unmet_heat_mwh": selected.unmet_heat,
        "pump_electricity_mwh": math.fsum(row.pump_electricity for row in rows),
        "electricity_purchased_mwh": math.fsum(row.electricity_purchased for row in rows),
        "boiler_heat_mwh": math.fsum(row.boiler_heat for row in rows),
        "heat_charged_mwh": math.fsum(item.charge for item in storage),
        "heat_discharged_mwh": math.fsum(item.discharge for item in storage),
        "retention_loss_mwh": math.fsum(item.retention_loss for item in storage),
        "charge_loss_mwh": math.fsum(item.charge_loss for item in storage),
        "discharge_loss_mwh": math.fsum(item.discharge_loss for item in storage),
        "min_soc_mwh": min(SOC, *(item.closing_soc for item in storage)),
        "max_soc_mwh": max(SOC, *(item.closing_soc for item in storage)),
        "terminal_soc_mwh": storage[-1].closing_soc,
        "max_balance_residuals_mwh": audit(hours, rows),
        "accepted_trace_constraint_violations": 0,
    }


def write_trace(path, hours, reference, selected):
    with path.open("wb") as stream, gzip.GzipFile(fileobj=stream, filename="", mode="wb", mtime=0) as archive:
        for index, hour in enumerate(hours):
            row = {"hour": index, "input": asdict(hour)}
            for label, selection in (("no_storage", reference), ("equal_resource_control", selected)):
                row[label] = {"dispatch": asdict(selection.schedule[index]),
                              "result": asdict(selection.hourly[index])}
            archive.write((json.dumps(row, separators=(",", ":"), allow_nan=False) + "\n").encode())


def export(output):
    output.mkdir()
    plant = Plant(STORAGE)
    summary = {
        "coordination_identifiable": False,
        "coordination_label_difference_before_overhead": 0,
        "assumed_overhead": OVERHEAD,
        "label_difference_after_assumed_overhead": -OVERHEAD,
        "initial_soc": SOC,
        "terminal_soc_target": SOC,
        "fuel_input": "not modeled; boiler useful heat reported",
        "schedule_candidates": ["no_shift", "adjacent_pair_pump_to_boiler"],
        "cases": {},
    }
    for scenario in SCENARIOS:
        hours = annual_hours(scenario)
        variants = {
            "main": (plant, hours),
            "zero_capacity": (replace(plant, storage=NO_STORAGE), hours),
            "zero_charge_rate": (replace(plant, storage=replace(STORAGE, charge_limit=0)), hours),
            "flat_price": (plant, tuple(replace(hour, price=65) for hour in hours)),
            "no_flexibility": (replace(plant, pump_limit=0), hours),
        }
        for name, (case_plant, case_hours) in variants.items():
            reference, selected, rejection = evaluate_case(case_plant, case_hours)
            key = f"{scenario}-{name}"
            write_trace(output / f"{key}.jsonl.gz", case_hours, reference, selected)
            summary["cases"][key] = {
                "hours": len(case_hours),
                "storage_plant": asdict(case_plant),
                "no_storage_plant": asdict(replace(case_plant, storage=NO_STORAGE)),
                "no_storage": summarize(case_hours, reference),
                "equal_resource_control": summarize(case_hours, selected),
                "flexibility_dispatch_savings": reference.dispatch_cost - selected.dispatch_cost,
                "rejected_shift_candidate": rejection,
            }
    (output / "summary.json").write_bytes((json.dumps(summary, indent=2, allow_nan=False) + "\n").encode())
    environment = {
        "python": sys.version,
        "platform": platform.platform(),
        "dependencies": "Python standard library only",
        "random_seed": None,
        "command": "py -E -S -B annual_storage.py OUTPUT_DIRECTORY",
        "argv": ["annual_storage.py", "OUTPUT_DIRECTORY"],
    }
    (output / "environment.json").write_bytes((json.dumps(environment, indent=2) + "\n").encode())
    manifest = "".join(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}\n"
                       for path in sorted(output.iterdir()))
    (output / "SHA256SUMS.txt").write_bytes(manifest.encode())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="a new directory for the replay artifacts")
    export(parser.parse_args().output)
