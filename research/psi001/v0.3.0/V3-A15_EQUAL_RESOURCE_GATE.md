# PSI-001 v0.3.0 — V3-A15 common-observation evidence and equal-resource acceptance

## Verified evidence
GitHub Actions run https://github.com/Open-Inquiry-Initiative/planetary-systems-integration/actions/runs/44723872264 completed successfully. The job log shows:
- Common snapshot payload: 105 UTF-8 JSON bytes for both methods.
- Bilateral: 167-byte observation envelope, 102-byte decision payload, 3 logical messages, 37.5 synthetic operating units.
- Coordinator: 169-byte observation envelope, 104-byte decision payload, 3 logical messages, 37.5 synthetic operating units.
- Gross operating gap: 0.
- `v3a14-common-observation.json` SHA256: `c13b4aeb7e6b9857695ec5760b125e80f1790661dfa970a512f7d19f132140ca`.
- Artifact retained by GitHub Actions for 90 days; checksum identifies this specific run's output.

## Equal-resource acceptance protocol
1. **Input parity:** A single immutable observation snapshot is the only input to each policy. Account for dissemination to every decision-maker, not just one labeled recipient.
2. **Wire parity:** Use identical field names, encoding and envelope schema; meter actual bytes across all links including observer, dispatcher and node-to-node exchanges. Message counts alone are insufficient.
3. **Decision parity:** Bound total decision rounds and deadlines. Record CPU-time distributions using repeated, interleaved samples on the same runner; never infer latency from a single process-local sample.
4. **Cost parity:** Apply the same heat physics and unit costs. Keep internal transfers out of total system costs. Specify and sweep communication cost per byte, per message and per millisecond as sensitivity assumptions until empirically measured.
5. **Falsification:** Retain price 40 zero-gap, price 80 fixed-price failure, zero link, zero surplus, and high pumping cost. Any positive mechanism advantage must survive fair baseline sensitivity and independent review.

## Gate decision
**V3-A14 observation-evidence subgate PASS.** **V3-A equal-resource scientific gate HOLD.** Equal snapshot content has been demonstrated, but not equal dissemination, topology, computation, deadlines or network costs. No claim of inherent coordination advantage or real-network resilience. Do not merge draft PR #10 or publish v0.3.0 yet.

## Next implementation
Build a canonical wire schema and an explicit topology-aware message ledger, including all observation deliveries and policy replies; add deterministic parity tests and a cost-sensitivity report.
