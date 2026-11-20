# PSI-001 v0.1.0 — Local release candidate readiness report

**State: LOCAL PACKAGE READY FOR MAINTAINER REVIEW; NOT PUBLISHED.**

This record summarizes the local operator/Codex report. The release package itself and its manifest have not been independently fetched or reviewed through this GitHub workflow.

## Reported verification
- 17/17 copied artifacts checked against their source files.
- 20/20 SHA-256 release manifest entries verified.
- Original experiment files still match their GATE-05 hashes.
- Package contains preserved annual and pilot source/results, GATE-06 reproduction metadata and logs, GATE-07 audit matrix and fixtures, and complete test output.
- Local privacy scan reported no credentials, personal identifiers or private absolute paths in included material.
- Sanitized execution excerpt limited to six scenario lines, timestamp and exit code.
- No scripts rerun during packaging; no upload, tag or release performed.

## Required release interpretation
The six original annual outputs reportedly reproduced byte-for-byte in a clean local environment. However:
- Two input-validation failures remain: silently dropped hours for mismatched series lengths, and negative base load permitting negative costs.
- Flat-tariff comparisons confound information/pricing with coordination; same hourly prices yield matched dispatch plus 100000 synthetic units coordination overhead.
- Heat-pump unavailability is not a validated physical thermal-trunk failure model.
- No scenario passed published 1% or later stated 5% threshold; later 5% provenance remains unverified.
- Reproducible computation is not evidence of causal coordination benefit.

## Publication blockers
1. **Maintainer licensing decision** for original source, fixtures and package content.
2. **Explicit authorization** to upload the reviewed local release package and create a public GitHub release.
3. Verify actual local package/manifest contents during upload; a summary report alone does not transfer them.

**Decision:** GATE-08 local packaging PASS reported; public release BLOCKED. Do not create a tag, merge as validated, or represent package as publicly available.
