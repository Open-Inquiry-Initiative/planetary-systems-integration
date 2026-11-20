# PSI-001 v0.3.0 — Coordination identification roadmap

**Status:** Research planning; no new findings. Branch starts at published v0.2.0 merge commit `3f39a703038d6baae419a5e5acf16f1ed31e4c8d`. Do not alter immutable v0.1.0 or v0.2.0 tags/assets.

## Research question
Does a distinct, physically feasible coordination policy provide incremental value over an independent policy when both have identical information, forecasts, equipment, energy balances and operating constraints, after accounting for coordination overhead?

## Preregistered gates
1. **V3-A — Identifiability specification:** Define a physically distinct coordination mechanism (e.g., sharing a constrained thermal loop across heterogeneous nodes) and independent baseline. Specify decision variables, observation sets, shared network constraints, dispatch horizon, information symmetry and operational overhead. Demonstrate on a hand-calculated small fixture where the policies can produce different feasible decisions. If no distinct mechanism exists, report unidentifiable and stop.
2. **V3-B — Conservative network model:** Model multiple heat sources/sinks, temperatures/quality constraints, heat loss, conversion efficiency, transport and pumping costs, thermal and electric energy conservation, capacity/ramp limits, unmet demand and optional storage. Both arms must use identical resources. Avoid double counting heat recovery.
3. **V3-C — Equal-information preregistration:** Fix datasets, scenarios, costs, forecast availability, policy definitions, optimization method, seeds, numerical tolerances, success criteria, sensitivity ranges and negative controls **before** evaluating results. Disallow tuning on the held-out evaluation set.
4. **V3-D — Controlled comparisons:** Compare independent versus coordinated dispatch with and without storage, overhead and constraints; include zero-link, zero-storage, flat-price, no-diversity and identical-policy controls. Record hourly traces, energy balances, unmet load, gross/net cost and computational burden.
5. **V3-E — Stress and generalization:** Ensure disruption windows overlap candidate coordination/storage operation; vary demand diversity, link capacity/loss, forecast error, network failure, tariff structure and overhead. Distinguish normal-operation savings from resilience outcomes.
6. **V3-F — Independent audit and release readiness:** Separate recomputation of balances and effects; rerun from clean environment; freeze source/data hashes; document limitations and license/privacy review. Publication requires explicit approval of exact release candidate.

## Primary estimand
Net coordination value = cost(independent, same resources/information) − cost(coordinated, same resources/information) − incremental coordination overhead. Also report gross savings, unmet-demand differences and separate storage value. Never infer a causal coordination effect from equal policies.

## Scientific guardrails
- v0.2.0's 6,077.82 synthetic-unit savings are a **storage flexibility** result; 196 active hours did not overlap disruption periods. They are not evidence for coordination or resilience.
- The 100,000-unit overhead in v0.2.0 is assumed, not measured. In v0.3.0 distinguish assumed scenario parameters from empirically estimated values.
- No physical network deployment, real-world efficiency, financial viability or resilience claims without appropriate evidence.
- Preserve all negative/failed results and exact reproducibility instructions.

## First deliverable
Produce `V3-A_IDENTIFIABILITY.md` with one minimal two-node hand-worked example, an independent baseline, a truly distinct coordination policy, equal information/resource assumptions, and at least one falsification test. Do not implement or report annual comparisons until V3-A passes.
