# PSI-001 v0.2.0 — Model Validation and Controlled Comparisons

**Status:** Planned; no new simulation or test results claimed.
**Baseline:** immutable public tag `psi-001-v0.1.0` at integration commit `914c363c4dc49eaf05032b0f8b9bb7269ef421c4`.
**Principle:** Preserve the original source, saved JSON, checksums and adverse findings. Implement fixes only in a new versioned source tree.

## Research question
Does coordinated electricity/heat dispatch provide a net economic or reliability benefit when both planners receive identical information, face the same equipment constraints, and are charged a transparent coordination overhead?

## Work packages
### V2-01 — Input contract and regression tests
- Require all hourly input series to have exactly the expected horizon length; reject truncation.
- Reject negative demand/base load, nonfinite values, invalid efficiencies, negative or impossible capacities and malformed scenarios.
- Add executable negative tests for unequal series lengths and negative base load, including the previously demonstrated negative-cost/service-met case.
- Document whether negative market prices are allowed separately from negative load.
- Re-run v0.1.0 six scenarios with new version and compare; any differences require a traceable explanation.

### V2-02 — Equal-information experimental design
- Specify identical hourly electricity/heat demand, tariff information, forecasts, heat-pump COP, capacities and outage schedule for both planners.
- Predefine Model A and Model B optimization/dispatch rules, information sets, constraints and coordination overhead.
- Run equal-information controls (including no-flexibility equivalence) and independently checked small fixtures.
- Separately vary information availability and coordination so tariff-information effects cannot be mislabeled coordination benefits.

### V2-03 — Explicit flexibility mechanisms
- Introduce candidate thermal storage, shifting, equipment ramp limits or network coupling **only as separately versioned model features**.
- Compare ablations: baseline, information-only, coordination-only, combined, with and without overhead.
- Measure costs, unmet load, energy balance, dispatch feasibility and constraint violations per hour.
- Avoid optimizing scenarios to force a positive result.

### V2-04 — Thermal-network outage realism
- Replace heat-pump-unavailability proxy with explicit network components/flow, capacity, losses and failure/recovery assumptions, or state clearly that physical resilience remains untested.
- Distinguish equipment outage, network outage and recovery cases.

### V2-05 — Reproducibility and release gate
- Export per-hour inputs, dispatch traces, model config, seeds, environment, SHA-256 manifest and exact commands.
- Predeclare primary metric, uncertainty/sensitivity plan and success threshold before looking at new outcomes; preserve the historical 1% threshold and unverified later 5% draft separately.
- Independent rerun, hand-calculated fixtures, adversarial validation, provenance/license/privacy review.
- Publish null and negative results with the same prominence as positive results.

## Acceptance gates
1. **GATE V2-A:** validation defects fixed; failing-input regression tests PASS.
2. **GATE V2-B:** equal-information comparison designed and preregistered; test harness passes.
3. **GATE V2-C:** hourly evidence and ablation outputs independently reproduced.
4. **GATE V2-D:** model limitations, sensitivity and network claims audited.
5. **GATE V2-E:** separately approved, licensed public release.

## First implementation task
Inspect the v0.1.0 original `psi001_annual.py` read-only, then copy it into a new v0.2.0 development directory. Implement strict input validation and executable regression fixtures. Do not change the published archive or tag. Report tests, exact commands, diffs and any unexpected behavior before proceeding to V2-B.
