# PSI-001 V2-B controlled comparison preregistration

This protocol is recorded before executing the V2-B harness. It uses the V2-A input contract and fixed-equipment model at commit 861e5042ad0e019674ef878d2f894078ec37bf0f.

## Four cells

| Decision price information | Independent dispatch | Coordinated dispatch control |
|---|---|---|
| Limited | Flat decision price of 65 in every hour | Same flat decision price and dispatch rule, plus coordination overhead |
| Shared hourly | Actual synthetic hourly price in each hour | Same hourly price and dispatch rule, plus coordination overhead |

In either row both planners receive identical electricity and heating loads, equipment availability, capacities, COP, and pricing information for the current hour. Neither planner uses future hours. Both are scored on the same realized hourly electricity prices even when the dispatch decision sees only the flat price. Both serve base electricity first, maximize feasible heat service second, and then minimize modeled dispatch cost using their decision price. A pump is cheaper at the margin when decision price < 45 × 2.5. At a tie, use the minimum pump draw consistent with maximum feasible heat service.

The model retains the V2-A 95 MWh/hour import ceiling, 18 MWh/hour pump-electricity ceiling, constant COP of 2.5, and 100 MWh/hour boiler ceiling at 45 synthetic currency units per MWh useful heat. Loads and prices come from the unchanged synthetic profile generator. Run the baseline, the 72-hour cold snap, and the 48-hour heat-pump-unavailability proxy as separate 8,760-hour scenarios. No storage, ramping, network coupling, demand shifting, or additional equipment is modeled.

Model A uses the existing hourly decision rule. Model B is a coordination-labeled control with the same feasible decisions, information, and optimization rule. There is no distinct coordination mechanism in V2-B. Its only additional charge is a fixed annual 100,000 synthetic currency units, added once per scenario. Report B without overhead as a separate accounting view. This design isolates information and bookkeeping effects; a null physical effect is structural. Any future test of a real coordination mechanism requires a separately specified model.

## Endpoints and contrasts

The primary endpoint is annual total cost after overhead. Also report pre-overhead dispatch cost, pump electricity, and unmet heat and electricity. Positive cost contrasts mean savings. For either cost measure, with A = independent, B = coordination control, L = limited, and H = shared hourly:

- Information-only savings = A(L) − A(H).
- Coordination-only savings = A(L) − B(L).
- Interaction savings = [B(L) − B(H)] − [A(L) − A(H)].
- Combined savings = A(L) − B(H), which must equal the sum of the three effects within absolute 1e-8 and relative 0.

Report every scenario, including zero and adverse effects. Compare physical outcomes within each information row for exact equality, and check both dispatch and total cost accounting. A hand-checkable flexible hour and a no-flexibility hour at the import ceiling must exercise the expected equality and accounting. No new coordination success threshold is introduced: the 1% published historical threshold belongs to the v0.1.0 analysis. This comparison cannot claim a coordination benefit without a distinct mechanism and a measured effect.