# PSI-001 — GATE-01 baseline freeze candidate (v0.1)

Status: **proposed, not yet frozen**. No simulation has been executed. This specification is for review before freezing inputs and running tests.

## Question and scope
For a synthetic region with 100,000 residents, 100 km², 500 GWh/year electricity demand and 300 GWh/year useful heating demand, does coordinated hourly electricity/district-heating dispatch reduce annualized total system cost by at least **5%**, inclusive of coordination overhead, without worsening service? These totals are synthetic targets, not observed measurements. First run excludes water, transportation, equipment sizing and siting optimization.

## Fixed common inputs
Publish an hourly 8,760-row synthetic-year dataset with UTC timestamps, electricity demand (MW), useful heat demand (MW_th), ambient temperature (°C), equipment availability, electricity import/export prices ($/MWh), fuel price ($/MWh_fuel), and disruption flags. Include a generation script, seed, units, SHA-256 checksums and generation assumptions. Both models receive the same information at the same hour and the same capacities, COP curve, efficiencies, line/thermal losses, storage state bounds, import limits, fuel limits and outage constraints. Use one identical objective-accounting ledger. No hindsight in one model unless both have it; use a declared rolling horizon or full-year perfect foresight identically.

## Model A: independent dispatch (locked candidate algorithm)
1. Electricity sector schedules non-heat electric demand, available generation and grid import/export, minimizing its own energy and operating cost subject to electrical balance, capacity and service limits. It publishes a residual electricity import capacity and a fixed hourly heat-pump electricity allocation.
2. The fixed heat-pump allocation is **the lesser of** (a) installed heat-pump electric nameplate and (b) nonnegative residual electric import-plus-generation headroom after non-heat load. It is computed by a published deterministic rule, not negotiated with heating. Electricity cannot reschedule its initial non-heat commitments in response to heating requests.
3. Heating minimizes its own cost using the allocated heat-pump electricity, fixed boiler/storage capacities and thermal network limits. Heating may use less than the allocation but may not request more. Unused allocation is released after heating dispatch, with no second optimization pass. All heat-pump electric consumption is booked as electricity-sector load at the same hour.
4. If capacity or service is infeasible, use explicitly modeled nonnegative unserved-electricity and unserved-heat slack variables, with identical large service-penalty coefficients and priority rules in A and B; report the actual unmet MWh separately. Never silently drop load.
5. Ties are resolved by stable asset identifier order; storage initial/final state and hourly loss conventions are identical. No sector can secretly access another sector's decision variables.

**Important review issue:** The fixed allocation above can be restrictive even where a jointly feasible solution exists. Report that structural disadvantage transparently, and include an optional sensitivity analysis with a stronger independently dispatched baseline (e.g., one published fixed tariff plus one-way market clearing). Do not quietly modify Model A after observing results.

## Model B: coordinated dispatch
Jointly optimize electricity and useful-heat scheduling with exactly the same equipment, physics, information horizon, service priorities and accounting. Model heat-pump input electricity explicitly, COP as a function of ambient temperature, heat distribution losses, thermal storage losses, and hourly balances. Add annual coordination overhead C_coord ($/year) to B's ledger, including declared software, communications, personnel and capital annualization assumptions. Compute break-even overhead = A system cost minus B system cost before overhead; negative values mean coordination cannot economically break even.

## Verification gates
- Hand-checkable 3–6 hour fixture with published inputs, expected balances and ledger.
- No-flexibility fixture: A and B must have equal service and cost before overhead to within tolerance.
- Full synthetic 8,760-hour base case.
- Predeclared cold-snap and thermal-trunk outage cases using identical shock timestamps and magnitudes for A and B.
- Hourly energy residual <= 1e-6 MWh or solver-appropriate normalized tolerance, whichever is stricter and feasible; document solver primal/dual gap and termination. Do not classify runs with material infeasibility as favorable.
- Store solver name/version, code commit, input hashes, seeds, wall-clock, solver status, configuration, and scenario results.

## Decision criteria (pre-registration proposal)
Cost improvement = (Cost_A - Cost_B_including_overhead) / Cost_A. Favorable only if improvement >= 5% **in the baseline case** and neither unserved electric nor unserved heat demand exceeds Model A in any reported scenario, with all declared absolute service ceilings met. Set absolute service ceilings and numerical tolerances before freeze; until then the gate is **not passed**. Report baseline, cold snap and trunk outage results independently; never conceal unfavorable scenarios. The 5% threshold is a research choice, not an externally validated standard.

## Freeze checklist
- [ ] Independent reviewer accepts Model A allocation/priority rule and stronger-baseline sensitivity plan
- [ ] Finalize equipment inventory, service ceilings, penalty coefficients, and solver tolerances
- [ ] Commit datasets, generator, scenario schedule and hashes
- [ ] Commit hand-checkable fixtures and expected results
- [ ] Record freeze commit SHA and prohibit post-result edits without versioned amendment
- [ ] Only then authorize execution

No numerical results, savings, validation or release readiness are claimed here.
