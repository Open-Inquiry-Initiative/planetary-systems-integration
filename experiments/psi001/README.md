# PSI-001 GATE-02 — executable input harness (candidate)

This directory contains a standard-library Python synthetic hourly dataset generator and one hand-checkable heat-pump balance fixture. **It does not implement either dispatch model, solve optimization, or establish cost savings.** No annual experiment results have been generated or validated as part of this commit.

## Reproduce

```sh
python3 experiments/psi001/generate_inputs.py --outdir generated/psi-001 --year 2025
```

The script writes `synthetic_hourly.csv` and `manifest.json` (including SHA-256). The CSV contains 8,760 UTC hourly records for a non-leap year, with synthetic electricity and heat loads normalized to 500,000 and 300,000 MWh respectively. Temperatures, tariffs and event flags are illustrative assumptions, not calibrated observations. Re-run twice and compare hashes to check deterministic output.

The single-hour fixture assumes 4 MWh non-heat electricity, 2 MWh heat-pump electricity, COP 3, 6 MWh useful heat, zero heat-network losses, and 6 MWh grid imports. Both hourly balance residuals must be zero. This fixture does not exercise dispatch optimization or nonzero distribution losses.

## Known blockers to baseline freeze and experiment execution

1. Fix equipment and storage parameters, network topology, heat-loss model, COP curve, import/export capacities, and the cost ledger.
2. Decide whether the Model A residual headroom rule is a defensible independent baseline, and specify its exact calculation under outages.
3. Fix service ceilings, unserved-energy penalties, cost accounting, 5% threshold, and numerical tolerances.
4. Implement actual independent and coordinated solvers with identical information and constraints; add no-flexibility equivalence tests and nonzero-loss fixtures.
5. Make cold snap and trunk outage flags change explicit physical constraints; their current presence in the CSV **does not** simulate a disruption.
6. Add automated tests and CI, execute and archive observed results with commit SHA and input hashes.

This is a **development milestone**, not a successful experimental result.
