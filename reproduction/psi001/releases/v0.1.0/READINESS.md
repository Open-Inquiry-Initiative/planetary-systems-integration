# PSI-001 v0.1.0 release readiness

**Decision: ready for local review. Public release is blocked pending a maintainer licensing decision and release authorization.**

| Check | Status | Evidence |
|---|---|---|
| Original integrity | PASS | Four original source/result files match their Gate-05 manifest by byte count and SHA-256. The Gate-05 ZIP and its eight entries match the verified preservation evidence. |
| Package integrity | PASS | All 17 copied files match their source artifacts. The release SHA-256 manifest covers every payload file, including the release documentation. |
| Numerical reproduction | PASS | Gate-06 recorded isolated CPython 3.15.2 on Windows 11, exit code 0, empty stderr, and byte-identical annual JSON across all six scenarios. |
| Audit evidence | PASS | Gate-07 matrix, unchanged hand-calculated fixtures, and complete captured test output are bundled. The audit confirms two input-validation failures and the pricing confound. |
| Privacy and sanitization | PASS for included files | Only listed Gate-05 through Gate-07 files and newly written release documentation are included. Text checks found no credentials, personal identifiers, or private absolute paths. The original session contribution is limited to six scenario lines, timestamp, and exit code. The verified nested ZIP contains those same reviewed Gate-05 files. |
| Licensing | BLOCKED | The packaged sources contain no license or SPDX notice. The PSI-001 and initiative landing repositories reported no recognized license and exposed no root license, copying, or notice file at review. The release owner needs to confirm rights and approve terms for the code, results, fixtures, and documentation before public distribution. |
| Scientific scope | LIMITED | Six reproduced synthetic scenarios, two verified malformed-input defects, and no isolated coordination advantage. The outage proxy cannot establish physical network resilience. The 5% draft provenance remains unverified and changes none of the six outcomes. |
| Publication | BLOCKED | The package is local and awaits explicit release authorization. This gate involved no script rerun, upload, tag, or publication. |

The source imports only Python standard-library modules and the audit fixtures also use the standard library. No third-party dependencies, private research archives, or full session logs are bundled.

[PSI-001 repository](https://github.com/Open-Inquiry-Initiative/planetary-systems-integration) · [Initiative landing repository](https://github.com/Open-Inquiry-Initiative/open-inquiry-initiative)
