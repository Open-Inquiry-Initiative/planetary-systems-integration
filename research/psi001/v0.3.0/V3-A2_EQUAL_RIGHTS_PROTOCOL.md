# PSI-001 v0.3.0 — V3-A2 equal-rights mechanism fixture

**Status:** Preregistered analytical comparison; not a passed simulation gate. Complements `V3-A_IDENTIFIABILITY.md`.

## Purpose
Separate the *value of enabling network exchange* from the *incremental value of a coordination protocol* when both arms can use the same link, observe the same data, and have the same physical resources.

## One-hour equal-rights fixture
Reuse the V3-A fixture: A has 10 MWh surplus usable heat; B requires 6 MWh; A→B link input cap 8 MWh, delivery efficiency 0.8; pumping cost 5 units/MWh input; B boiler costs 100 units/MWh delivered. Both policies may dispatch any link flow x in [0, 7.5] and meet the remaining B demand by boiler. Both know all values.

Total cost as function of link flow x: C(x) = 5x + 100(6 − 0.8x) = 600 − 75x. Minimum occurs at x=7.5, giving cost 37.5. Any deterministic policy that globally minimizes this same cost under identical constraints must select x=7.5, regardless of whether its solver is labeled decentralized or centralized.

- **Independent/decentralized arm:** A and B can negotiate exchange using a posted per-MWh-input transfer price p with full information. A offers any available otherwise-curtailed heat at nonnegative price; B buys up to x=7.5 if its avoided boiler cost per input MWh (80 units) exceeds the combined transfer price plus pumping charge. Select a preregistered price p=40 units/MWh input. A supplies x=7.5; B accepts; total *system* cost 37.5 (internal transfer payment 300 cancels).
- **Coordinated arm:** A system dispatcher directly minimizes C(x), selecting x=7.5 and cost 37.5.
- **Equal-rights mechanism effect:** 37.5 − 37.5 = **0 synthetic units before incremental protocol overhead**. The mechanisms differ (price-mediated bilateral trade versus centralized dispatch), but both achieve the same feasible physical flow. This is a valid zero-result control, not evidence of positive coordination value.
- **Network exchange effect:** 600 − 37.5 = 562.5 units versus a separately labeled no-exchange control. Do not attribute it to central coordination.

## What could make mechanisms differ?
For a testable positive or negative difference, preregister a bounded decentralized protocol with an explicit operational limitation *that is itself the object of study*, such as limited negotiation rounds, message delays, asynchronous local decisions, or local price updates. Compare against a coordinator with **the same underlying observation set, link rights, computational budget, time budget and communication accounting**; any extra global communication must be measured and charged, not hidden. Distinguish performance under constrained communication from claims of intrinsic centralization advantage.

## Falsification controls
1. Both protocols have enough rounds/time to converge: expect zero gap in this linear fixture.
2. Same fixed feasible flow imposed on both: expect zero cost gap.
3. Zero link or zero surplus: expect zero exchange value and zero mechanism gap.
4. Account for internal transfer payments only as transfers, not system-wide economic costs.
5. If a positive mechanism gap appears in an unconstrained exact-solver comparison, flag a likely implementation, accounting or information mismatch.

## Acceptance conditions for V3-A
- Implement deterministic tests for cost function, conservation, caps, bilateral-price dispatch and centralized optimum.
- Demonstrate equal-rights zero-gap fixture and at least one preregistered, operationally constrained protocol case with auditable message/computation costs and equal information availability.
- Independently verify all fixtures and record the distinction between network exchange, protocol performance and net coordination value.
- Do not advance to annual claims or V3-B until independent checks pass.

**Current status:** The zero-gap equal-rights analytical control is specified; implementation and independent validation are pending.
