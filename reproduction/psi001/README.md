# PSI-001 — GATE-04 reproducibility package

**Status: package structure prepared; source artifacts missing; reproduction NOT run.**

This package is intended to make the previously published six comparisons independently reproducible. It must not substitute a newly written model for the original implementation and claim equivalence.

## Published reference
https://github.com/Open-Inquiry-Initiative/open-inquiry-initiative/blob/main/PROJECTS.md#psi-001-synthetic-dispatch-experiment

Published net savings (synthetic currency units, includes assumed annual 100,000-unit coordination overhead):

| Scenario | Independent flat tariff | Independent hourly tariff |
|---|---:|---:|
| Baseline | 272995 | -100000 |
| Cold snap | 271751 | -100000 |
| Thermal-trunk proxy | 268045 | -100000 |

Published interpretation: no case meets the published 1% net savings threshold. The 5% proposal in a later draft is a separate, unmerged candidate and must not be retroactively substituted.

## Artifact intake checklist

Place the *original* experiment files, not approximations, under a versioned release directory:
- `source/`: actual Model A and B dispatch implementations, dependency lockfile, license
- `inputs/`: synthetic 8760-hour dataset, generator, equipment and tariff parameters, outage schedules
- `configs/`: all six exact run configurations and threshold provenance
- `expected/`: original detailed machine-readable output for all six cases, hourly energy balances, costs, unmet load
- `logs/`: original execution logs, environment details and solver versions
- `manifest.json`: SHA-256 for every input and expected-output file, original source commit, command lines and units

Before uploading, scan for secrets, personal identifiers, licensed third-party content and absolute local paths. Never fabricate hashes or outputs to complete the manifest.

## Independent reproduction protocol

1. Check out the immutable original source revision; record platform, interpreter and solver versions.
2. Verify every SHA-256 against the release manifest.
3. Execute all six scenario/tariff combinations with the exact original settings and record exit codes, stdout/stderr, runtime, and numerical status.
4. Check hourly electrical and useful-heat balances, COP, network losses and unserved load; publish maximum absolute residuals.
5. Compare annualized A and B cost components and net savings against expected machine-readable values, using explicitly documented numeric tolerances.
6. Confirm no-flexibility equivalence in a separate fixture; compare hourly dispatch under shared price information.
7. Report **PASS / FAIL / INCONCLUSIVE** for each scenario; preserve discrepancies as evidence rather than editing expected outputs.
8. Publish the independent runner's environment, command transcript, resulting hashes, and review sign-off.

## Required evidence reconciliation
- Exact timing and provenance of the 1% threshold decision.
- Whether Model A's tariff and exchange rule was fixed before execution.
- Distinction between an actual thermal-trunk failure and the published heat-pump-unavailability proxy.
- Original overhead calculation and denominator for savings percentage.
- Whether any deviations exist between original experiment source and the GATE-01/02 draft proposals.

## Release criteria

Do not mark this gate complete or tag a validated release until original source, data and outputs are published and independently rerun. An unverified release candidate may be labeled **reproduction pending** only.

Related review: https://github.com/Open-Inquiry-Initiative/planetary-systems-integration/pull/3
