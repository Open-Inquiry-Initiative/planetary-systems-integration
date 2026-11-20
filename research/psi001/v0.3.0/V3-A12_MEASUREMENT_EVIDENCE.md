# PSI-001 v0.3.0 — V3-A12 measurement evidence and fairness gate

**Evidence:** GitHub Actions run https://github.com/Open-Inquiry-Initiative/planetary-systems-integration/actions/runs/44719047168 completed successfully for V3-A11 measurement workflow. Companion V3-A tests also passed in run 44719047192.

## Observed fixture output
- Bilateral: 2 logical messages; 102 UTF-8 serialized payload bytes; operating cost 37.5 synthetic units; flow 7.5 MWh input.
- Coordinator: 2 logical messages; 104 UTF-8 serialized payload bytes; operating cost 37.5 synthetic units; flow 7.5 MWh input.
- Gross operating-cost gap: 0. Payload difference (bilateral minus coordinator): -2 bytes.
- Local measured execution: bilateral 66,523,917 ns total / 10,000 iterations = 6,652.3917 ns average; coordinator 62,304,845 ns total / 10,000 = 6,230.4845 ns average.
- Evidence hashes recorded by CI: `v3a11-independent-sweep.json` SHA256 `5488aef2c956a8015a383e7d7f8a97b99bfb7506c6faec4a6c2dd26cbaa6d587`; `v3a11-measurements.json` SHA256 `ffcc757cafec96e1d983eb054791d7f72172355670b7f167dfff12867a900539`. GitHub Actions artifacts have 90-day retention; these hashes refer to the original run's files, not future reruns.

## Interpretation and caveats
The instrumentation measures process-local Python execution and UTF-8 JSON *payload* bytes only; it does not measure network transit, packet overhead, queueing, serialization at remote endpoints, hardware power use, or monetized communication costs. The coordinator's request/response and the bilateral offer/accept are not information-equivalent transactions merely because each has two messages. Both methods were stipulated to know fixture data before decisions, and that acquisition was not metered. Timing is a single unpaired sample and is not evidence of a statistically significant speed difference.

## Fairness gate: HOLD
Before a causal equal-resource claim:
1. Define a common observation snapshot and account for how each method receives it.
2. Use a common wire schema and meter every input, decision and response; record byte counts and logical rounds, including any broadcast.
3. Fix deadlines and CPU/compute budgets or explicitly vary them symmetrically.
4. Pre-register a sensitivity sweep over prices, message limits, and overhead coefficients; preserve zero-gap and failure controls.
5. Have an independent reviewer validate protocol parity and reproduce the evidence.

**Decision:** V3-A11 measurement evidence PASS; V3-A equal-resource scientific gate HOLD. No general coordination benefit or real-network resilience established. No v0.3.0 merge/release authorized.
