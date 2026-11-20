# PSI-001 GATE-06 — Independent six-case rerun

**Status: PREPARED / BLOCKED. No independent rerun has occurred.**

Prerequisite: GATE-05 must recover and verify original source, six configurations, input checksums and expected outputs. The published summary alone is insufficient.

## Run protocol
1. Independent operator uses a fresh checkout of the original experiment commit, with no locally modified files.
2. Verify original source and input SHA-256 manifest before execution. Record OS, runtime, dependency/solver versions, hardware, commands and exit codes.
3. Execute baseline, cold snap and heat-pump-unavailability trunk proxy, each with independent-planner flat and hourly tariffs: six cases.
4. Capture per-hour Model A and B dispatch, grid/fuel usage, delivered heat, unserved demand, cost components and solver status; archive stdout/stderr.
5. Compare exact results to archived original outputs using a documented tolerance, separately comparing rounded published net savings 272995, 271751, 268045 and -100000 for each hourly-price case.
6. Record discrepancies without modifying the original outputs. Produce a signed report with PASS / FAIL / INCONCLUSIVE for every case.

## Required exit evidence
- [ ] Verified GATE-05 source and manifest
- [ ] Independent run log for each of six cases
- [ ] Raw machine-readable independent results and hashes
- [ ] Comparison report with numeric tolerances and status per case
- [ ] Operator and reviewer sign-off

**Do not mark PASS based on the comparison utility alone; it checks only published rounded savings, not model physics or independent provenance.**
