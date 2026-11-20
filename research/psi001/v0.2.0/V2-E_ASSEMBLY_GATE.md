# PSI-001 v0.2.0 — Candidate assembly execution gate

**Status:** Authorized for candidate preparation, **not assembled or released**.
**Authorization:** `V2-E_AUTHORIZATION.md`.
**Evidence review:** user-reported 62 existing files with pinned SHA-256 hashes and five planned additions; inventory must be retrieved from the original V2-E review before execution. **Do not reconstruct the inventory by guessing from PR paths.**

## Deterministic assembly procedure
1. Retrieve the exact reviewed 67-file inventory and the original 62 pinned SHA-256 values. Record source commit SHA, path, expected digest, license classification and whether each file is new. Stop if inventory or digests are missing.
2. Materialize the 62 existing files from their pinned source revisions, not from mutable branch tips. Verify SHA-256 byte-for-byte against inventory **before** assembling additions.
3. Prepare exactly five reviewed additions; include explicit scoped MIT license/copyright notice, applicable inherited v0.1.0 notices, Codex assistance disclosure and sanitized verification note as specified in inventory. Do not silently add extra files. Review all five for privacy and licensing.
4. Exclude the raw C4 verification log containing a private absolute path; search the final payload for private paths, personal identifiers, credentials and third-party restricted content. Do not include private raw log as an appendix or nested archive entry.
5. Produce candidate in a separate staging directory; generate a canonical sorted SHA-256 manifest, source-revision provenance, 67-file count report, reproduction commands, environment and all limitations. Verify archives recursively, including ZIP contents.
6. Independently extract/re-read the candidate and verify all 67 hashes and nested archive hashes. Run tests/replay in clean environment if practical and report exact command, exit status, interpreter and results. No silent fixes to scientific artifacts.
7. Verify v0.1.0 tag and 24 release artifacts remain unchanged, including eight nested ZIP entries. Keep PR #9 draft.
8. Report candidate location, digest, complete PASS/FAIL/BLOCKED checklist and any deviation. **Do not merge, tag, create GitHub Release or publish** without approval of the exact assembled candidate.

## Attribution and limitations required in release notes
- Copyright 2026 Brandon J Lemon for user-owned new v0.2.0 material; MIT, with inherited v0.1.0 notices retained.
- Codex assistance disclosed.
- Annual storage flexibility under fixed candidate schedules: 6,077.82 synthetic units in each of three main scenarios; 196 storage-active hours did not overlap disruptions.
- Coordination effect is unidentifiable; 100,000 synthetic-unit overhead is an assumption; investment costs excluded; physical network resilience untested.
- Negative controls and sensitivity outcomes retained prominently.

**Blocker:** The final package cannot be called verified until the complete pinned inventory, five additions and independent post-assembly checksum report are present.
