#!/usr/bin/env python3
"""PSI-001 GATE-02: deterministic synthetic input generator and balance fixture.

Standard-library only. This is NOT a dispatch optimizer or a cost comparison.
"""
import argparse
import csv
import hashlib
import json
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path

FIELDS = ("timestamp_utc", "electric_demand_mw", "useful_heat_demand_mw",
          "ambient_c", "grid_import_price_usd_per_mwh",
          "fuel_price_usd_per_mwh_fuel", "cold_snap", "trunk_outage")

def generate(outdir: Path, year: int = 2025):
    if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
        raise ValueError("Use a non-leap synthetic year for the 8760-hour fixture")
    outdir.mkdir(parents=True, exist_ok=True)
    start = datetime(year, 1, 1, tzinfo=timezone.utc)
    rows = []
    for hour in range(8760):
        dt = start + timedelta(hours=hour)
        season = math.cos(2 * math.pi * (dt.timetuple().tm_yday - 15) / 365)
        diurnal = math.sin(2 * math.pi * dt.hour / 24)
        temp = 12 - 13 * season + 4 * diurnal
        electric_shape = 1 + 0.12 * diurnal + 0.10 * season
        heat_shape = max(0.08, 1 + 0.75 * season - 0.12 * diurnal)
        rows.append([dt.isoformat().replace("+00:00", "Z"), electric_shape,
                     heat_shape, temp, 90.0, 35.0,
                     int(hour in range(24 * 20, 24 * 23)),
                     int(hour in range(24 * 45, 24 * 46))])
    e_scale = 500000.0 / sum(r[1] for r in rows)
    h_scale = 300000.0 / sum(r[2] for r in rows)
    path = outdir / "synthetic_hourly.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(FIELDS)
        for r in rows:
            writer.writerow([r[0], f"{r[1]*e_scale:.12f}", f"{r[2]*h_scale:.12f}",
                             f"{r[3]:.8f}", r[4], r[5], r[6], r[7]])
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    manifest = {
        "project": "PSI-001", "gate": "GATE-02", "status": "synthetic-input-only",
        "year": year, "hours": len(rows), "time_step_hours": 1,
        "target_electric_mwh": 500000, "target_useful_heat_mwh": 300000,
        "cold_snap_hours": [480, 551], "trunk_outage_hours": [1080, 1103],
        "sha256_synthetic_hourly_csv": digest,
        "notes": "Scenario flags are labels; impacts require a separate fixed equipment model."
    }
    (outdir / "manifest.json").write_text(json.dumps(manifest, indent=2)+"\n")
    return manifest

def check_fixture():
    """Independent hand-checkable one-hour energy ledger, not optimized."""
    nonheat_electric_mwh = 4.0
    useful_heat_mwh = 6.0
    heat_pump_electric_mwh = 2.0
    heat_pump_cop = 3.0
    grid_import_mwh = 6.0
    heat_distribution_loss_mwh = 0.0
    electricity_residual = grid_import_mwh - nonheat_electric_mwh - heat_pump_electric_mwh
    heat_residual = heat_pump_electric_mwh * heat_pump_cop - useful_heat_mwh - heat_distribution_loss_mwh
    assert abs(electricity_residual) < 1e-9
    assert abs(heat_residual) < 1e-9
    return {"fixture": "one_hour_heat_pump", "electricity_residual_mwh": electricity_residual,
            "heat_residual_mwh": heat_residual, "verified": True}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", default="generated/psi-001")
    parser.add_argument("--year", type=int, default=2025)
    args = parser.parse_args()
    print(json.dumps({"fixture": check_fixture(),
                      "generated": generate(Path(args.outdir), args.year)}, indent=2))
