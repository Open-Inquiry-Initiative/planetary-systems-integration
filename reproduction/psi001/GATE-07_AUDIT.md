# PSI-001 GATE-07 — Methodology and numerical audit

**Status: PREPARED / BLOCKED. No independent audit performed.**

Prerequisites: verified GATE-05 artifacts and completed GATE-06 reruns.

## Audit matrix
- Model A: identify fixed electricity–heat exchange rule, sector scheduling order, infeasibility handling, tariff information, and evidence these were set before results.
- Model B: verify the same equipment, capacity, demand, outage, service requirements and dispatch information; document any information asymmetry.
- Physics: check hourly electric and heat balances, COP, thermal losses, heat-pump input energy, unserved MWh and outage availability.
- Numerical: check solver optimality/feasibility status, objective values, tolerances, tie-breaking, rounding and sensitivity.
- Costs: verify all fuel/grid/operating charges, annual coordination overhead of 100000 synthetic units, cost denominator and net-savings formula.
- Threshold: reconcile published 1% criterion with later draft 5% proposal; do not claim preregistration without timestamped proof.
- Limits: no storage, ramping or endogenous equipment selection; thermal-trunk outage was represented by heat-pump unavailability; synthetic data are not field validation.
- Robustness: hand-checkable energy balance, no-flexibility equivalence, and shared-hourly-price dispatch equivalence fixture.

## Decision
For each audit item report PASS / FAIL / INCONCLUSIVE with exact evidence references. Any failure affecting validity blocks a verified release. Preserve unfavorable outcomes and unresolved limitations.

- [ ] All material findings supported by source, test or run artifact
- [ ] Independent reviewer signs the audit
- [ ] Failures addressed by a new version or explicitly disclosed as unresolved
