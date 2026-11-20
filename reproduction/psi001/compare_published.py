#!/usr/bin/env python3
"""Check the published PSI-001 summary against a separately reproduced results JSON.

No model is run here. Expected results are the publicly reported rounded net savings.
A successful comparison does NOT establish independent reproduction by itself.
"""
import argparse
import json
from pathlib import Path

EXPECTED = {
    "baseline": {"flat": 272995, "hourly": -100000},
    "cold_snap": {"flat": 271751, "hourly": -100000},
    "trunk_proxy": {"flat": 268045, "hourly": -100000},
}

def compare(path: Path, absolute_tolerance: float):
    data = json.loads(path.read_text(encoding="utf-8"))
    results = data["scenarios"]
    failures = []
    for scenario, tariffs in EXPECTED.items():
        for tariff, expected in tariffs.items():
            try:
                actual = float(results[scenario][tariff]["net_savings"])
            except (KeyError, TypeError, ValueError) as exc:
                failures.append(f"{scenario}/{tariff}: missing or invalid: {exc}")
                continue
            if not (abs(actual - expected) <= absolute_tolerance):
                failures.append(f"{scenario}/{tariff}: {actual} differs from {expected}")
    return failures

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("results_json", type=Path,
                   help="Independently generated results; not included in this repository yet")
    p.add_argument("--absolute-tolerance", type=float, default=0.5,
                   help="Default 0.5 synthetic units for nearest-integer rounded publication")
    args = p.parse_args()
    if args.absolute_tolerance < 0:
        p.error("tolerance must be nonnegative")
    errors = compare(args.results_json, args.absolute_tolerance)
    print(json.dumps({"comparison": "published_rounded_net_savings_only",
                      "passed": not errors, "errors": errors}, indent=2))
    raise SystemExit(1 if errors else 0)
