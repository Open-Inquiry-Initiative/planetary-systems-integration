# PSI-001 V2-C preregistration — constrained thermal-storage mechanism

**Status:** Design frozen before V2-C implementation/execution. This document contains no V2-C results.
**Parent evidence:** V2-A validation and V2-B factorial control at commit `606729162de5a215abd160fa9d54ad883f565eaa`.
**Scope:** Synthetic dispatch economics; **not** a physical district-heating network or resilience validation.

## Causal question and fair comparator
Can access to **a defined thermal-storage scheduling mechanism** reduce realized annual dispatch costs relative to an otherwise identical, independently operated reference, under identical hourly forecasts, demand, market prices, capacities and service obligations? Distinguish **value of storage/flexibility** from **value of coordination**: if only the coordinated arm receives storage, the difference is a resource-access effect, **not** isolated coordination. The primary fair test gives both arms the same storage and physical constraints; only permitted cross-system coordination decisions differ. If no genuinely different, implementable policy can be specified, report coordination **not identifiable**, not a benefit.

## Model and controls
- Deterministic hourly state of charge `S[t]` in MWh thermal, with `0 <= S[t] <= capacity`; bounded charge/discharge rates, charging/discharging efficiencies in (0,1], optional hourly retention in [0,1], and explicit thermal-energy balance.
- Declare heat production, electrical consumption (including heat-pump COP), storage charging/discharging, losses and heat delivered at each hour. No simultaneous charge/discharge unless explicitly justified and modeled.
- Enforce electricity and heat service, equipment availability, heat-pump/boiler limits and outages. Record unmet demand separately; never hide infeasibility with an implicit backup.
- Use same realized prices for scoring every arm. Both arms see identical forecasts and information; keep information-only factorial contrast separate.
- Define and justify any coordinated policy **before** observing results; baseline and coordinated policies must have equal storage access. Add a storage-absent control and a zero-capacity equivalence test.
- Use identical initial and terminal storage state (or price terminal energy at an explicit common value), avoiding free energy at horizon boundaries. State whether perfect foresight is assumed.
- Keep the historic 100,000 synthetic currency overhead as a separately reported assumed cost, not a measured engineering cost.

## Preregistered comparisons
1. No-storage reference, both arms identical (negative control).
2. Storage available to both arms, independent vs coordinated **policy-only** contrast (primary mechanism-isolation test).
3. Storage available to only one arm (resource-access illustration, **not** coordination evidence).
4. Ablations for capacity=0, charge rate=0, efficiency losses, no time-varying price, and overhead=0.
5. Run baseline, cold snap, and heat-pump outage proxy with unchanged synthetic input generation; do not call the outage proxy a trunk failure.

## Primary and secondary outcomes
Primary: paired annual net-cost difference `cost_independent - cost_coordinated`, after explicit overhead, in synthetic currency units, with dispatch-cost difference reported separately. Secondary: unmet MWh electricity/heat, constraint violations, storage cycles/throughput, terminal SOC, heat-pump electricity, fuel use and per-hour balance residuals. Positive net savings require positive primary contrast and zero constraint violations; report sensitivity rather than infer population-level significance from three deterministic scenarios. No newly invented success threshold.

## Verification and reporting gate
- Hand-worked 2–4-hour examples for SOC, losses, COP, tariffs, terminal state and feasibility.
- Property tests for conservation, rate/capacity bounds, nonnegative demand, no hidden imports, finite outputs, and zero-storage equivalence.
- Export hourly inputs, schedules, SOC, costs, residuals, configs, exact commands, interpreter version and SHA-256 hashes; independently reproduce outputs.
- Keep V2-A 13 tests and V2-B 5 additional tests passing.
- Present all negative/null results and any model-identifiability limitation.
- Preserve v0.1.0 tag and artifacts; do not merge PR #9 or publish V2-C until review.

## Implementation order
**C1:** implement isolated storage state transition + tests. **C2:** integrate storage with energy balances and hand fixtures. **C3:** specify truly distinct equal-resource dispatch policies, or explicitly mark coordination unidentifiable. **C4:** run preregistered scenarios, ablations and reproducibility checks.
