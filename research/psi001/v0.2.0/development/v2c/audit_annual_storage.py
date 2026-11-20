"""Read-only audit of C4 exports and separately labeled one-factor sensitivities."""
import argparse
from dataclasses import replace
import gzip
import hashlib
import json
import math
from pathlib import Path
import platform
import sys


TOL = 1e-9
ORIGINAL_MANIFEST = "828ab7f7d376f8484857d57fbb0906f3d2ffc56324c74bfb5b67867aad5d5a23"
SCENARIOS = ("baseline", "cold_snap", "heat_pump_outage_proxy")
VARIANTS = ("main", "zero_capacity", "zero_charge_rate", "flat_price", "no_flexibility")
ARMS = ("no_storage", "equal_resource_control")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_manifest(directory):
    manifest = directory / "SHA256SUMS.txt"
    if digest(manifest) != ORIGINAL_MANIFEST:
        raise ValueError("C4 manifest does not match its recorded digest")
    expected = {f"{s}-{v}.jsonl.gz" for s in SCENARIOS for v in VARIANTS}
    expected.update(("summary.json", "environment.json"))
    seen = set()
    for line in manifest.read_text(encoding="utf-8").splitlines():
        sha, name = line.split("  ", 1)
        if name not in expected or name in seen or digest(directory / name) != sha:
            raise ValueError(f"C4 checksum or inventory mismatch: {name}")
        seen.add(name)
    if expected != seen or {p.name for p in directory.iterdir()} != seen | {manifest.name}:
        raise ValueError("C4 file inventory differs")
    return ORIGINAL_MANIFEST


def close(actual, expected, field):
    if not math.isclose(actual, expected, rel_tol=0, abs_tol=TOL):
        raise ValueError(f"{field}: observed {actual!r}, expected {expected!r}")
    return abs(actual - expected)


def audit_hour(cfg, hour, arm, opening):
    flow, row = arm["dispatch"], arm["result"]
    s = row["storage"]
    tank = cfg["storage"]
    charge, discharge = flow["charge"], flow["discharge"]
    pump, boiler = flow["pump_electricity"], flow["boiler_heat"]
    imports = cfg["import_limit"] if hour["grid_available"] else 0
    base = min(hour["electric_load"], imports)
    pump_limit = min(cfg["pump_limit"], imports - base) if hour["pump_available"] else 0
    boiler_limit = cfg["boiler_limit"] if hour["boiler_available"] else 0
    for amount, bound, label in (
        (pump, pump_limit, "pump/import"), (boiler, boiler_limit, "boiler"),
        (charge, tank["charge_limit"], "charge"), (discharge, tank["discharge_limit"], "discharge"),
        (opening, tank["capacity"], "opening SOC"), (s["closing_soc"], tank["capacity"], "closing SOC"),
    ):
        if not math.isfinite(amount) or not 0 <= amount <= bound + TOL:
            raise ValueError(f"invalid {label} bound or availability")
    if (charge and discharge) or ((not hour["storage_available"] or tank["capacity"] == 0)
                                  and (charge or discharge)):
        raise ValueError("invalid storage transfer")
    retained = opening * tank["retention"]
    withdrawal = discharge / tank["discharge_efficiency"]
    stored = charge * tank["charge_efficiency"]
    if withdrawal > retained + TOL:
        raise ValueError("storage withdrawal exceeds retained SOC")
    losses = (opening - retained, charge - stored, withdrawal - discharge)
    closing = opening + charge - discharge - math.fsum(losses)
    produced = pump * cfg["cop"] + boiler
    available_heat = produced + discharge - charge
    if charge > produced + TOL or available_heat > hour["heat_load"] + TOL:
        raise ValueError("unbacked charge or unmodeled heat dumping")
    delivered = min(available_heat, hour["heat_load"])
    purchased = base + pump
    electric_cost = purchased * hour["price"]
    boiler_cost = boiler * cfg["boiler_cost"]
    expected_row = {
        "pump_electricity": pump, "pump_heat": pump * cfg["cop"], "boiler_heat": boiler,
        "heat_produced": produced, "heat_delivered": delivered, "electricity_purchased": purchased,
        "base_electricity_served": base, "electricity_cost": electric_cost,
        "boiler_cost": boiler_cost, "realized_cost": electric_cost + boiler_cost,
        "unmet_electricity": hour["electric_load"] - base, "unmet_heat": hour["heat_load"] - delivered,
        "heat_balance_residual": available_heat - delivered,
        "electricity_balance_residual": purchased - base - pump,
    }
    expected_storage = {
        "opening_soc": opening, "closing_soc": closing, "charge": charge, "discharge": discharge,
        "retention_loss": losses[0], "charge_loss": losses[1], "discharge_loss": losses[2],
        "balance_residual": 0,
    }
    deviations = [close(row[key], value, key) for key, value in expected_row.items()]
    deviations.extend(close(s[key], value, key) for key, value in expected_storage.items())
    for residual in (
        math.fsum((row["electricity_purchased"], row["unmet_electricity"],
                   -hour["electric_load"], -pump)),
        math.fsum((produced, opening, -row["heat_delivered"], -s["closing_soc"],
                   -s["retention_loss"], -s["charge_loss"], -s["discharge_loss"])),
    ):
        deviations.append(close(residual, 0, "boundary conservation"))
    return max(deviations)


def inspect_case(path, saved):
    plant_key = {"no_storage": "no_storage_plant", "equal_resource_control": "storage_plant"}
    fields = {"dispatch_cost": "realized_cost", "unmet_electricity_mwh": "unmet_electricity",
              "unmet_heat_mwh": "unmet_heat", "pump_electricity_mwh": "pump_electricity",
              "electricity_purchased_mwh": "electricity_purchased", "boiler_heat_mwh": "boiler_heat"}
    storage_fields = {"heat_charged_mwh": "charge", "heat_discharged_mwh": "discharge",
                      "retention_loss_mwh": "retention_loss", "charge_loss_mwh": "charge_loss",
                      "discharge_loss_mwh": "discharge_loss"}
    state = dict.fromkeys(ARMS, 0)
    peak = dict.fromkeys(ARMS, 0)
    minimum = dict.fromkeys(ARMS, 0)
    total_fields = fields.keys() | storage_fields.keys()
    series = {arm: {field: [] for field in total_fields} for arm in ARMS}
    max_deviation = 0
    hourly_inputs = []
    active = []
    paired_savings = []
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        for index, line in enumerate(stream):
            trace = json.loads(line)
            if trace["hour"] != index:
                raise ValueError(f"nonconsecutive hour in {path.name}")
            hour = trace["input"]
            hourly_inputs.append(hour)
            for arm in ARMS:
                packed = trace[arm]
                row = packed["result"]
                try:
                    deviation = audit_hour(saved[plant_key[arm]], hour, packed, state[arm])
                except ValueError as error:
                    raise ValueError(f"{path.name} hour {index} {arm}: {error}") from error
                max_deviation = max(max_deviation, deviation)
                state[arm] = row["storage"]["closing_soc"]
                peak[arm] = max(peak[arm], state[arm])
                minimum[arm] = min(minimum[arm], state[arm])
                for key, source in fields.items():
                    series[arm][key].append(row[source])
                for key, source in storage_fields.items():
                    series[arm][key].append(row["storage"][source])
            a, b = (trace[label]["result"] for label in ARMS)
            delta = a["realized_cost"] - b["realized_cost"]
            paired_savings.append(delta)
            if b["storage"]["charge"] or b["storage"]["discharge"]:
                active.append({"hour": index, **hour, **trace[ARMS[1]]["dispatch"],
                               "cost_difference": delta})
    if len(hourly_inputs) != 8760 or saved["hours"] != len(hourly_inputs):
        raise ValueError(f"incorrect annual horizon in {path.name}")
    for arm in ARMS:
        close(state[arm], 0, "terminal SOC")
        close(state[arm], saved[arm]["terminal_soc_mwh"], "reported terminal SOC")
        close(peak[arm], saved[arm]["max_soc_mwh"], "reported peak SOC")
        close(minimum[arm], saved[arm]["min_soc_mwh"], "reported minimum SOC")
        for key, values in series[arm].items():
            close(math.fsum(values), saved[arm][key], f"{arm} {key}")
    active_hours = {record["hour"] for record in active}
    outside_storage = math.fsum(delta for i, delta in enumerate(paired_savings)
                               if i not in active_hours)
    paired = math.fsum(paired_savings)
    if not math.isclose(paired, saved["flexibility_dispatch_savings"], rel_tol=0, abs_tol=1e-7):
        raise ValueError(f"paired savings mismatch in {path.name}")
    return {"max_deviation_mwh_or_currency": max_deviation, "active": active,
            "paired_cost_savings": paired,
            "paired_savings_outside_active_hours": outside_storage,
            "unmet_heat_mwh": math.fsum(series[ARMS[1]]["unmet_heat_mwh"])}, hourly_inputs


def audit_archives(original, replay):
    hashes = [verify_manifest(directory) for directory in (original, replay)]
    summary = json.loads((original / "summary.json").read_bytes())
    if (summary["initial_soc"], summary["terminal_soc_target"]) != (0, 0):
        raise ValueError("unexpected SOC targets")
    cases = {}
    main_inputs = {}
    for case, saved in summary["cases"].items():
        evidence, inputs = inspect_case(original / f"{case}.jsonl.gz", saved)
        cases[case] = evidence
        if case.endswith("-main"):
            main_inputs[case] = inputs
    baseline = "baseline-main"
    overlap = {}
    for scenario, inputs in main_inputs.items():
        base_inputs = main_inputs[baseline]
        changed = {field: [i for i, (a, b) in enumerate(zip(base_inputs, inputs, strict=True))
                           if a[field] != b[field]] for field in base_inputs[0]}
        active_hours = {record["hour"] for record in cases[scenario]["active"]}
        overlap[scenario] = {
            "changed_hours": changed,
            "active_hours_overlapping_any_input_change": sorted(active_hours.intersection(
                i for hours in changed.values() for i in hours)),
            "active_records_equal_to_baseline": cases[scenario]["active"] == cases[baseline]["active"],
        }
    return {"original_and_replay_manifest_sha256": hashes, "cases": cases, "overlap": overlap}


def sensitivities():
    # The independent archival audit above does not import the C4 solver.
    from annual_storage import STORAGE, Plant, annual_hours, evaluate_case

    base = Plant(STORAGE)
    variants = {
        "c4_reference": ({}, None),
        "capacity_4": ({"capacity": 4}, None),
        "capacity_32": ({"capacity": 32}, None),
        "charge_efficiency_0.5": ({"charge_efficiency": 0.5}, None),
        "discharge_efficiency_0.5": ({"discharge_efficiency": 0.5}, None),
        "lossless_conversion": ({"charge_efficiency": 1.0, "discharge_efficiency": 1.0}, None),
        "retention_0.5": ({"retention": 0.5}, None),
        "retention_1": ({"retention": 1.0}, None),
        "charge_limit_4": ({"charge_limit": 4}, None),
        "charge_limit_12": ({"charge_limit": 12}, None),
        "discharge_limit_2": ({"discharge_limit": 2}, None),
        "discharge_limit_12": ({"discharge_limit": 12}, None),
        "flat_tariff_65": ({}, "flat"),
        "half_evening_premium": ({}, "half_evening"),
    }
    results = {}
    for scenario in SCENARIOS:
        hours = annual_hours(scenario)
        results[scenario] = {}
        for label, (storage_changes, tariff) in variants.items():
            plant = replace(base, storage=replace(STORAGE, **storage_changes))
            current = hours
            if tariff == "flat":
                current = tuple(replace(h, price=65) for h in hours)
            elif tariff == "half_evening":
                current = tuple(replace(h, price=h.price - 35) if 17 <= i % 24 < 22 else h
                                for i, h in enumerate(hours))
            reference, selected, rejected = evaluate_case(plant, current)
            results[scenario][label] = {
                "storage_overrides": storage_changes,
                "tariff_override": tariff,
                "storage_savings": reference.dispatch_cost - selected.dispatch_cost,
                "reference_cost": reference.dispatch_cost,
                "selected_cost": selected.dispatch_cost,
                "selected_candidate": selected.candidate_index,
                "charged_mwh": math.fsum(r.storage.charge for r in selected.hourly),
                "reference_unmet_heat_mwh": reference.unmet_heat,
                "selected_unmet_heat_mwh": selected.unmet_heat,
                "reference_unmet_electricity_mwh": reference.unmet_electricity,
                "selected_unmet_electricity_mwh": selected.unmet_electricity,
                "rejected_candidate": rejected,
            }
    overhead = [{"assumed_overhead": value, "label_difference_pre_overhead": 0,
                 "label_difference_after_overhead": -value}
                for value in (0, 5_000, 10_000, 100_000)]
    return {"coordination_identifiable": False, "storage_sensitivity": results,
            "overhead_accounting_only": overhead}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("original", type=Path)
    parser.add_argument("replay", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    record = {"archival_audit": audit_archives(args.original, args.replay),
              "exploratory_sensitivities": sensitivities(),
              "environment": {"python": sys.version, "platform": platform.platform(),
                              "dependencies": "Python standard library only"}}
    with args.output.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(record, stream, indent=2, allow_nan=False)
        stream.write("\n")


if __name__ == "__main__":
    main()
