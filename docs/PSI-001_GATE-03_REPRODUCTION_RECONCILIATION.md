# PSI-001 — GATE-03 methodology reconciliation and reproduction

**Status:** documentation and evidence intake started; independent reproduction **not performed**. This record does not revise the published results or claim that an earlier preregistration was satisfied.

## Provenance and observed publication

- Public result summary: https://github.com/Open-Inquiry-Initiative/open-inquiry-initiative/blob/main/PROJECTS.md#psi-001-synthetic-dispatch-experiment
- Public result publication commit: https://github.com/Open-Inquiry-Initiative/open-inquiry-initiative/commit/c1fc02174ac49e8d18bf3cf06dcfd16a161de178
- Original conceptual protocol: `docs/EXPERIMENT_PROTOCOL.md` on main.
- Later GATE-01 candidate: https://github.com/Open-Inquiry-Initiative/planetary-systems-integration/pull/1 (draft, not merged).
- Later GATE-02 generator candidate: https://github.com/Open-Inquiry-Initiative/planetary-systems-integration/pull/2 (draft, not merged).
- The published simulation source and detailed machine-readable outputs are reported as **local only**. Their revision, solver, input checksums, and run log have not been verified here.

## Reported results (synthetic currency units, net of 100,000 annual coordination overhead)

| Scenario | Flat-tariff Model A | Hourly-price Model A |
|---|---:|---:|
| Baseline | +272,995 | -100,000 |
| 72-hour cold snap | +271,751 | -100,000 |
| 48-hour heat-pump-unavailability proxy for trunk outage | +268,045 | -100,000 |

Reported flat-tariff savings: approximately 0.57–0.58%, below the **published 1% threshold**. When both planners had the same hourly prices, reported dispatch matched and net savings were negative. All demand was reportedly served. These are **published claims**, not independently reproduced values.

## Methodology discrepancy register

| ID | Issue | Required evidence | Status |
|---|---|---|---|
| M-01 | 1% threshold in published campaign vs 5% in later GATE-01 proposal | Timestamped configuration, original protocol/commit history, decision log identifying whether 1% was set before results | Open |
| M-02 | Exact independent dispatch and exchange rules | Source and configuration for Model A, tariff schedule, dispatch order, infeasibility handling | Open |
| M-03 | Identical physical and service constraints | Equipment table, COP, loss accounting, capacities, unserved demand handling, price information | Open |
| M-04 | Thermal trunk outage represented by heat-pump unavailability | Explain proxy limitations and physical alternatives | Open |
| M-05 | No storage/ramping and fixed equipment | Document excluded flexibility; do not generalize beyond model | Recorded limitation |
| M-06 | Cost denominator and coordination overhead | Per-scenario A and B gross costs, overhead ledger, exact savings formula | Open |
| M-07 | Reproduction and numerical validity | Source revision, input checksums, runtime, solver version, tolerances, independent run outputs | Open |

**Threshold policy:** Do not substitute 5% for the reported 1%, or imply the 1% criterion was preregistered, without timestamped evidence. Preserve both as distinct historical proposals/decisions. A reproduction tests the reported calculation as-is; a new prospective experiment requires a separately frozen threshold.

## Reproduction acceptance procedure (pending source publication)

1. Archive source code, requirements/lockfile, environment, input generation and files, equipment and tariff tables, scenario definitions, and exact command lines at an immutable commit or release.
2. Publish expected per-scenario machine-readable results including total A cost, total B cost before/after overhead, electric/heat unserved MWh, energy-balance residuals, and dispatch comparisons.
3. Have an independent runner clone a clean checkout, verify hashes, execute the six scenario/tariff combinations, and record stdout/stderr, exit codes, solver status, versions and timestamps.
4. Compare reproduced values to published values at the stated precision; investigate discrepancies before declaring success. Test no-flexibility equivalence and hand-checkable energy balances separately.
5. Publish an evidence table with pass/fail/inconclusive per scenario. Report any deviation and amended code as a **new version**, never silently overwrite the initial campaign.

## Gate exit criteria

- [ ] Exact original local experiment artifacts preserved and made available for review
- [ ] M-01 through M-07 reconciled with evidence and citations
- [ ] All six cases independently rerun from clean source
- [ ] Numeric reconciliation and physical/service checks passed or discrepancies published
- [ ] Reviewed public release includes limits and negative outcomes

Until those items are satisfied, **GATE-03 remains open**.
