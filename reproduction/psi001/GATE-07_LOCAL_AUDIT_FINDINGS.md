# PSI-001 — GATE-07 local scientific audit findings

**Status:** Local audit reported complete; **conditional/failing scientific review**, not an unconditional PASS. Supporting source, fixtures and complete test output remain local and have not been independently inspected here.

## Reproducibility and tests
- All six annual results remain byte-for-byte identical to archive.
- Hand-calculated fixtures reported PASS: electricity/heat balance, COP, dispatch, cost accounting, unmet demand, cold-snap boundary and heat-pump-unavailability outage boundary.
- Original and archived hashes reported unchanged after audit.

## Confirmed defects (not observed in six archived runs)
1. **FAIL — input series length mismatch:** silently truncates hours; must reject mismatched lengths explicitly and add a regression test.
2. **FAIL — negative base load:** permits negative costs while reporting demand served; must reject negative demand and add a regression test.

Do not edit historical source/results. Fixes belong to a separately versioned model with original behavior preserved.

## Interpretation limitations
- **FAIL for causal attribution:** flat-tariff Model A versus coordinated Model B does not isolate the value of coordination because information/pricing assumptions differ. Under equal hourly prices dispatch matched and Model B incurred 100000 synthetic currency units of coordination overhead.
- **INCONCLUSIVE:** physical thermal-trunk resilience. The modeled outage is heat-pump unavailability, not a detailed thermal network failure.
- Published 1% threshold confirmed in source, archived JSON and public project map. Later 5% draft provenance unverified; cannot retroactively claim it was predeclared.
- No scenario exceeded either 1% or 5%.

## Release disposition
**GATE-07 audit performed, with material FAIL and INCONCLUSIVE findings. GATE-08 verified scientific release is BLOCKED.** A transparent *research archive with limitations* may be prepared after artifacts are reviewed, but must not be labeled validated causal evidence.

## Outstanding evidence
Publish sanitized audit matrix/report, fixtures, test commands/output and checksums after privacy/license review. Preserve original source and raw results unmodified.
