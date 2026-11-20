# PSI-001 GATE-08 — Reviewed reproducible research release

**Status: RELEASE CHECKLIST ONLY. NOT VALIDATED OR RELEASED.**

This is a prospective release process, not evidence that GATE-05–07 have passed.

## Release contents
- Immutable original experiment source revision, license and dependency lockfile
- Inputs, equipment, tariff and outage configurations with units and SHA-256 checksums
- All six original and independently reproduced result sets, per-hour ledgers and logs
- Independent rerun report (GATE-06) and methodology/numerical audit (GATE-07)
- Explicit provenance of the published 1% threshold and distinct later 5% draft
- Public results including negative outcomes and exact coordination overhead assumptions
- Known limits, including synthetic data, fixed equipment, no storage/ramping and outage proxy
- Reproduction commands and environment details

## Publication controls
1. Confirm GATE-05, GATE-06 and GATE-07 have documented PASS status, or explicitly withhold verified status.
2. Complete privacy, secrets, license and third-party content review.
3. Review exact release tree and checksums; do not alter historical expected outputs.
4. Obtain reviewer approval; then create immutable version tag and GitHub release.
5. Update public project map with verified status **only after** successful independent reproduction and audit.
6. If prerequisites fail, publish an evidence-gap report instead of a verified release.

- [ ] Original artifacts available and verified
- [ ] Six independent runs completed
- [ ] Numerical and methodology audit passed
- [ ] Public reproducibility materials reviewed
- [ ] Immutable release created and linked

**No release tag or verified-reproduction claim is authorized by this draft.**
