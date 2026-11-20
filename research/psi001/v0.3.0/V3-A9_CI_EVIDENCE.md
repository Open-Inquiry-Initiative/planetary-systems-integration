# PSI-001 v0.3.0 — V3-A9 CI evidence record

**Evidence class:** GitHub-hosted automated test execution, not external peer review.

- Source commit under test: `2fef9a8abf6cbda2a0e846e74ce8fa7d2e07af8f`
- GitHub Actions run: https://github.com/Open-Inquiry-Initiative/planetary-systems-integration/actions/runs/44706386426
- Run ID: `44706386426`; job ID: `136186916300`; run number: 12
- Event: PR merge-ref checkout observed at `17e4e9acbed3666749b0cab3dcb55b6f8b0bfb45` (test source includes the head commit)
- Environment: GitHub-hosted Ubuntu, CPython 3.12.16
- Command: `python -m unittest discover -s research/psi001/v0.3.0/development -p 'test_v3a*.py' -v`
- Observed log summary: **Ran 17 tests in 0.001s — OK**
- Breakdown: 9 baseline fixture tests, 5 bounded-protocol tests, 3 independent Decimal-auditor tests; each test line reported `ok`.
- CI conclusion: `success`, including the test execution step.
- Provenance: recorded from GitHub Actions job logs, not manually inferred from workflow success alone.

## Interpretation and limitations

The independent Decimal implementation reproduces the stipulated six price-sweep outcomes under deterministic assertions. No independent external reviewer, measured message bytes, elapsed decision time, empirical thermal network, or protocol overhead is established. The one-round fixed-price protocol can fail under unfavorable prices; this is not evidence of inherent centralization superiority. The published v0.1.0/v0.2.0 artifacts are outside this PR.

## Gate decision

**V3-A deterministic fixture and CI subgate: PASS.**
**V3-A complete scientific gate: HOLD.** Remaining: measured/equal communication budget and overhead, independent reviewer or separately reproduced audit artifacts, and explicit fairness check of the coordinator's inputs. Do not merge/release v0.3.0 or start V3-B on the strength of these unit tests alone.

## Follow-up
Introduce instrumented message serialization and a comparable communication schedule for both methods; log byte counts and timing in a reproducible harness, then rerun controls. Archive raw outputs and hashes before requesting review.
