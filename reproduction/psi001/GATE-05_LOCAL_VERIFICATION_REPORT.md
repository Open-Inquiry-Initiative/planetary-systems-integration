# PSI-001 — GATE-05 local verification report (operator-reported)

**Evidence status:** Local operator/Codex reported completion; original package is still local and was **not** inspected by the GitHub-side assistant. Do not treat this report as independently validated hashes or a published artifact release.

## Located and preserved
- Original `psi001_annual.py` and `psi001_annual_results.json`
- Original `psi001_pilot.py` and `psi001_pilot_results.json`
- SHA-256 manifest, embedded configuration and assumptions, and sanitized six-line execution excerpt
- Byte-for-byte copies reported to match original hashes; originals untouched

## Saved annual results (synthetic currency units)
| Scenario | Flat tariff net savings | Hourly-price net savings |
|---|---:|---:|
| Baseline | 272995 | -100000 |
| Cold snap | 271751 | -100000 |
| Thermal-trunk outage proxy | 268045 | -100000 |

Operator reported: all six cost and service checks passed; zero unmet demand in both models for all six; no case achieved the published 1% savings threshold. Net savings recomputed from archived costs matched rounded published values.

## Remaining evidence gaps
- Original package and its actual hashes have not been transferred or reviewed here.
- No independent execution has occurred.
- Source generates hourly inputs in memory; no exported hourly inputs or per-hour dispatch ledger identified.
- Dedicated original execution log absent; sanitized session excerpt retained.
- Threshold chronology (1% published vs later 5% draft) still requires provenance review.

## Gate decision
**GATE-05: local verification reported PASS; repository-level artifact intake and independent review PENDING.**
Do not advance GATE-06 from protocol to PASS until an independent rerun and comparison report exist.
