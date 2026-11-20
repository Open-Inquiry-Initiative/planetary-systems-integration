# PSI-001 GATE-05 — Original artifact recovery and verification

**Gate status: BLOCKED ON ORIGINAL LOCAL ARTIFACTS.** This checklist and scanner are prepared; neither local recovery nor original source validation has occurred. Do not describe GATE-05 as complete until all exit criteria are met.

## Scope and custody
Recover the exact source, configuration, inputs, logs and detailed outputs that produced the six published comparisons, preserving original timestamps and checksums where possible. Do not substitute the GATE-02 illustrative generator or reconstruct missing outputs and label them original.

## Operator procedure
1. On the machine containing the original run, locate the PSI-001 source directory, six scenario outputs, tariff and equipment configurations, environment details and logs. Do not search unrelated personal folders or upload them.
2. Copy artifacts into a dedicated *private* staging directory. Preserve originals untouched.
3. Run `python3 reproduction/psi001/inventory_artifacts.py /path/to/private/staging --output /path/to/private/inventory.json` to generate a SHA-256 inventory. Review all paths and content for secrets, tokens, personal data, absolute host paths and third-party licensing before publishing.
4. Create a release manifest mapping each scenario/tariff combination to source revision, command, input hash, output hash, model assumptions, threshold history and cost accounting. Use `UNKNOWN` rather than invent missing provenance.
5. Verify that each of six runs has raw A/B cost components, overhead, service metrics and energy-balance diagnostics; confirm that the published rounded values can be calculated from the raw outputs.
6. Have a second reviewer verify hashes and provenance. Record any absent or conflicting files in a discrepancy register.
7. Only after review, publish the approved artifact package to the appropriate repository and link it from this record.

## Exit criteria
- [ ] Original local artifacts found and preserved
- [ ] Inventory and hashes generated from originals
- [ ] All six cases trace to original source, inputs and outputs
- [ ] Secrets/privacy/license review completed
- [ ] Threshold discrepancy and Model A rules traced to evidence, or explicitly marked unresolved
- [ ] Reviewed package published and accessible
- [ ] Independent reviewer signs off on completeness

**Current evidence:** public summary in Open-Inquiry-Initiative/open-inquiry-initiative at commit c1fc021; original simulation source and detailed outputs remain reported local and were not available to this GitHub-only operation.

## Downstream gates
GATE-06 independent rerun; GATE-07 numerical/methodology audit; GATE-08 reviewed reproducible release. No automatic advancement on the strength of a file inventory alone.
