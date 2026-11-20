# PSI-001 v0.3.0 — V3-A7 independent interpretation audit

**Status:** CI evidence verified; analytical audit protocol committed. Independent rerun of all traces and an independent code-level audit remain to be completed.

## CI provenance
GitHub Actions run 44706241476 for commit `58d87f68b2767c14c1a4d8e3dc29fabcb4ea553d` completed successfully. The fixture job and test step were successful. The configured test discovery includes both `test_v3a_fixture.py` (9 tests) and `test_v3a_bounded_protocol.py` (5 tests). A successful job is evidence that the suite exited successfully, not a substitute for independent reimplementation.

## Preregistered expected price sweep
Under the stipulated one-hour fixture: 6 MWh demand, 10 MWh surplus, 8 MWh link capacity, 0.8 delivery efficiency, 5 units/MWh-input pumping cost, 100 units/MWh-delivered boiler cost. The centralized optimum is x=7.5 MWh input, with 6 MWh delivered and 37.5 synthetic units of operating cost.

| Price (units/input MWh) | Bilateral response | Bilateral flow (MWh input) | Bilateral cost | Central cost | Gross protocol gap |
|---:|---|---:|---:|---:|---:|
| 0 | Accept | 7.5 | 37.5 | 37.5 | 0 |
| 40 | Accept | 7.5 | 37.5 | 37.5 | 0 |
| 74.99 | Accept | 7.5 | 37.5 | 37.5 | 0 |
| 75 | Reject (tie) | 0 | 600 | 37.5 | 562.5 |
| 80 | Reject | 0 | 600 | 37.5 | 562.5 |
| 100 | Reject | 0 | 600 | 37.5 | 562.5 |

For each row, bilateral sends exactly two logical messages: posted price and accept/reject. Message *bytes*, measured latency and overhead are not implemented or measured. The price is a transfer between nodes and cancels in system cost.

## Audit requirements
1. Recompute all six rows **without importing the implementation under audit**. Check threshold: buyer avoids 0.8×100=80 units of boiler per MWh input, pays 5 pumping; accept iff price <75.
2. Reconcile energy: at x=7.5, delivered 6, lost 1.5, boiler 0, curtailed 2.5. At x=0, boiler 6, curtailed 10. All link and supply caps respected.
3. Verify two logical messages per row and no hidden extra exchanges. Do not call them equivalent *byte* or latency budgets.
4. Verify zero-link and no-surplus controls; tie handling at 75; input validation for nonfinite/negative prices and infeasible flows.
5. Verify published v0.1.0/v0.2.0 tags and release artifacts remain unchanged.
6. Preserve independent rerun command, Python version, test output, code SHA and audit artifact digests.

## Interpretation and next decision
- **Supported analytically:** In this *specified* one-round, fixed-price protocol, rejected trades produce a gross gap of 562.5 synthetic units; accepted trades yield zero gap.
- **Not supported:** Inherent centralization superiority, positive net value after communication overhead, measured timing/byte parity, robustness, resilience, or real-world performance.
- **Gate:** V3-A cannot be declared complete until an independent rerun/reimplementation confirms these controls and the operationally constrained comparison is documented without information/resource asymmetry. Advance to V3-B only after that check.
