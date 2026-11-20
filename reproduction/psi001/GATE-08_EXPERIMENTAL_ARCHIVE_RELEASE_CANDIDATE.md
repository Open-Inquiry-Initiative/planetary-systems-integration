# PSI-001 — GATE-08 release candidate: experimental archive

**Status: PREPUBLICATION / EVIDENCE PACKAGE LOCAL. Not a validated scientific release.**

## Intended public release designation
PSI-001 v0.1.0 — Reproduced Synthetic Experiment (Audited Limitations)

## Abstract
A synthetic 8760-hour electricity/heat dispatch experiment compared independent and coordinated planners under two price-information settings. Six original saved annual results were reportedly reproduced byte-for-byte on Windows 11 with CPython 3.15.2 and standard-library dependencies only. Local audit fixtures passed basic balance, COP, dispatch, cost and outage-proxy checks. The experiment does **not** demonstrate an isolated causal coordination benefit.

## Published net savings (synthetic currency units)
| Scenario | Flat-tariff independent planner | Hourly-price independent planner |
|---|---:|---:|
| Baseline | +272995 | -100000 |
| Cold snap | +271751 | -100000 |
| Heat-pump-unavailability outage proxy | +268045 | -100000 |

Annual coordination overhead: 100000 synthetic units. All six archived results reported zero unmet demand. No scenario passed the published 1% savings criterion.

## Required limitations statement
1. Flat-tariff comparison confounds tariff information with planner coordination; it cannot isolate coordination's causal contribution.
2. With the same hourly prices, dispatch matched; coordination incurred overhead and was net costlier.
3. Original model lacks strict validation for mismatched input-series lengths (silent dropped hours) and negative base load (negative costs with apparently served demand). Neither failure was observed in archived six cases. Both must be repaired in a separate version, preserving the original.
4. Outage represents heat-pump unavailability; physical thermal-trunk resilience remains untested.
5. Synthetic fixed-equipment setting; no storage or ramping; results do not generalize to field operations.
6. Published 1% criterion confirmed in local source, JSON and public map. Later 5% draft provenance unverified.
7. Exact local rerun and audit are **operator-reported**; original files, checksum manifests, execution logs, fixtures and test outputs are not yet independently inspected or published through this GitHub workflow.
8. Original annual output is a summary; no per-hour dispatch export identified.

## Prepublication release checklist
- [ ] Review sanitized package directory, inventory, checksums and license
- [ ] Inspect original source and archived JSON against manifest
- [ ] Include clean rerun JSON, execution metadata, stdout/stderr, comparison report
- [ ] Include full audit matrix, hand-checkable fixture code and test outputs
- [ ] Redact credentials, unrelated conversation material, user paths and personal identifiers
- [ ] Confirm no source/results changed during packaging
- [ ] Independent reviewer checks release contents and evidence links
- [ ] Publish with **experimental archive / not causal validation** designation
- [ ] Create immutable tag only after review and approval
- [ ] Update public project map with scope and limitations, not an unqualified PASS

**Gate disposition:** release candidate documentation ready; actual release blocked until package review. Verified-scientific-release gate remains failed/inconclusive pending model revisions and new tests.
