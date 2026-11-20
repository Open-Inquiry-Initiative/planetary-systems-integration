"""Independent, hand-calculated tests for the preserved PSI-001 model."""
import hashlib
import json
from pathlib import Path
import platform
import runpy

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "PSI-001-GATE-05" / "psi001_annual.py"
ARCHIVE = ROOT / "PSI-001-GATE-05" / "psi001_annual_results.json"
RERUN = ROOT / "PSI-001-GATE-06" / "annual-rerun.json"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot():
    original_paths = tuple(p for p in (ROOT / "PSI-001-GATE-05").iterdir() if p.is_file())
    top_level_originals = tuple(ROOT.glob("psi001_*"))
    return {path: digest(path) for path in
            (*original_paths, *top_level_originals, RERUN, ROOT / "PSI-001-GATE-05.zip")}


def main():
    before = snapshot()
    assert before[SOURCE] == "4f9e2113b4e9a641dd04987d2dc801b6b34a8505d4eb24715795e03a5611a03a"
    assert before[ARCHIVE] == before[RERUN] == "d2cf48d7714606b882fe49216ab6342af5224c3b0991727e51f7d6120a935add"
    assert ARCHIVE.read_bytes() == RERUN.read_bytes()
    run = runpy.run_path(str(SOURCE))["run"]
    print(platform.python_version(), platform.platform())
    print("INTEGRITY: preserved source and both 4,959-byte JSON files match pinned hashes.")

    def case(electric, heat, price, hours=1, scenario="baseline", shared=True):
        tariff = (lambda hour, value: value) if shared else (lambda hour, value: 65)
        return run(scenario, tariff, [electric] * hours, [heat] * hours, [price] * hours)

    def signature(record, planner):
        row = record[planner]
        return tuple(row[key] for key in ("pump_electric_mwh", "dispatch_cost",
                                          "unserved_electric_mwh", "unserved_heat_mwh"))

    def check(name, record, a, b):
        assert signature(record, "independent") == a, (name, record)
        assert signature(record, "coordinated") == b, (name, record)
        assert record["independent"]["total_cost"] == a[1]
        assert record["coordinated"]["total_cost"] == b[1] + 100_000
        assert record["net_savings"] == a[1] - b[1] - 100_000
        assert record["service_met"] == (max(*a[2:], *b[2:]) <= 1e-8)
        print(f"PASS {name}: A={a} B={b} net={record['net_savings']:g}")

    print("Fixture tuples: (pump MWh, dispatch cost, unmet electricity MWh, unmet heat MWh)")
    check("import cap and COP", case(90, 20, 40), (5, 4137.5, 0, 0), (5, 4137.5, 0, 0))
    check("pump nameplate cap", case(10, 60, 40), (18, 1795, 0, 0), (18, 1795, 0, 0))
    check("boiler cap takes precedence over expensive electricity",
          case(10, 120, 130), (8, 6840, 0, 0), (8, 6840, 0, 0))
    check("no flexibility, different price signals",
          case(95, 20, 40, shared=False), (0, 4700, 0, 0), (0, 4700, 0, 0))
    check("shared hourly prices with flexibility",
          case(10, 25, 130), (0, 2425, 0, 0), (0, 2425, 0, 0))
    check("different tariffs with flexibility",
          case(10, 25, 130, shared=False), (10, 2600, 0, 0), (0, 2425, 0, 0))
    check("exact marginal cost tie", case(10, 25, 112.5),
          (0, 2250, 0, 0), (0, 2250, 0, 0))
    stress = case(100, 130, 130)
    check("capacity shortfall", stress, (0, 16850, 5, 30), (0, 16850, 5, 30))
    assert not stress["service_met"] and not stress["favorable"]
    check("48-hour outage boundary", case(10, 25, 40, 48, "thermal_trunk_outage"),
          (0, 73200, 0, 0), (0, 73200, 0, 0))
    check("hour 49 after outage", case(10, 25, 40, 49, "thermal_trunk_outage"),
          (10, 74000, 0, 0), (10, 74000, 0, 0))
    cold = case(10, 20, 40, 73, "cold_snap")
    assert abs(cold["heat_demand_mwh"] - 1892) < 1e-8
    assert abs(cold["coordinated"]["pump_electric_mwh"] - 756.8) < 1e-8
    assert abs(cold["coordinated"]["dispatch_cost"] - 59472) < 1e-8
    print(f"PASS cold snap boundary: heat={cold['heat_demand_mwh']:g} pump={cold['coordinated']['pump_electric_mwh']:g} dispatch={cold['coordinated']['dispatch_cost']:g}")

    truncated = run("baseline", lambda h, p: p, [10, 10], [25], [40, 40])
    assert truncated["heat_demand_mwh"] == 25 and truncated["service_met"]
    print("FAIL input-length validation: two electric and price intervals, one heat interval; one interval silently dropped and service_met=True.")
    negative = case(-5, 0, 40)
    assert negative["independent"]["dispatch_cost"] == -200 and negative["service_met"]
    print("FAIL input-domain validation: negative base load yields dispatch cost -200 and service_met=True.")

    saved = json.loads(ARCHIVE.read_bytes())
    assert set(saved["campaigns"]) == {"flat_tariff", "hourly_tariff"}
    assert saved["minimum_net_savings_share"] == 0.01
    expected_rounded = {"baseline": 272995, "cold_snap": 271751, "thermal_trunk_outage": 268045}
    for tariff, scenarios in saved["campaigns"].items():
        assert set(scenarios) == set(expected_rounded)
        for scenario, record in scenarios.items():
            a, b = record["independent"], record["coordinated"]
            assert abs(a["total_cost"] - a["dispatch_cost"]) < 1e-8
            assert abs(b["total_cost"] - b["dispatch_cost"] - 100_000) < 1e-8
            assert abs(a["total_cost"] - b["total_cost"] - record["net_savings"]) < 1e-8
            assert abs(a["dispatch_cost"] - b["dispatch_cost"] - record["break_even_overhead"]) < 1e-8
            assert abs(a["total_cost"] * 0.01 - record["minimum_net_savings"]) < 1e-8
            assert all(row[field] == 0 for row in (a, b) for field in
                       ("unserved_electric_mwh", "unserved_heat_mwh"))
            assert record["service_met"] and not record["favorable"]
            assert round(record["net_savings"]) == (expected_rounded[scenario] if tariff == "flat_tariff" else -100_000)
            share = record["net_savings"] / a["total_cost"]
            assert share < 0.01 and share < 0.05
            print(f"PASS saved {tariff}/{scenario}: net={record['net_savings']:.9f} share={share:.6%} unmet=0, 1% and 5% both fail")

    assert snapshot() == before
    print("INTEGRITY: original, archived, and Gate-06 artifact hashes unchanged.")


if __name__ == "__main__":
    main()
