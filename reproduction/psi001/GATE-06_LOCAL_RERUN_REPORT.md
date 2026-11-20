# PSI-001 — GATE-06 local independent rerun report

**Status:** Operator/Codex reports PASS on local Windows environment. Original and rerun files remain local; this repository record is a report of verification, not independent inspection of the artifacts.

## Execution
- Fresh working directory; isolated CPython 3.15.2, Windows 11
- Python standard library only
- Exit code: 0; stderr: empty
- Source copy and all four preserved originals checked against SHA-256 hashes before execution
- Original source files and GATE-05 archive checked unchanged afterward

## Comparison
- Rerun JSON reported byte-for-byte identical to archived original
- All six scenarios matched for every saved JSON field, including planner dispatch/total costs, net savings and unmet electricity and heat demand
- Absolute and relative result-comparison tolerances: 0
- Model internal energy balance and service tolerance: 1e-8
- Reported numerical differences: 0

## Evidence custody
Local artifacts reported: reproduction report, execution metadata, complete stdout, rerun results and stderr log. They have not been uploaded or reviewed in this GitHub workflow. No independent confirmation of hashes or byte equality has been performed here.

## Scientific boundaries
Exact computational reproduction of the saved annual output does not validate the model's assumptions, the adequacy of Model A, physical balance implementation, or the interpretation of the 1% threshold. The published results remain below that threshold. Hourly inputs and dispatch traces were not exported in the original artifacts.

## Gate decision
**GATE-06 local PASS reported. Public artifact verification PENDING.** Proceed to GATE-07 source-level audit and numerical/methodology review; retain draft PR until evidence is reviewed.
