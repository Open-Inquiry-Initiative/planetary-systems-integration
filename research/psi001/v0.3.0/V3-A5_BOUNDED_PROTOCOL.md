# PSI-001 v0.3.0 — V3-A5 bounded communication protocol

**Status:** Preregistered design only; no results. V3-A4 fixture CI completed successfully (GitHub Actions run 44706021342).

## Causal target
Measure the *protocol-performance gap under bounded communication*, not a universal advantage of centralized control. Compare two methods with the same information availability, physical exchange rights, total message budget, decision deadline and computation budget. Log the actual messages and costs, not just nominal allowances.

## Minimal two-node protocol test
Use the existing one-hour fixture. A and B both know the same demand, supply, link capacity, loss, boiler cost and pumping cost before dispatch. Both can exchange heat. A protocol may only choose a feasible transfer x; evaluation uses the same physical cost function for both.

**Decentralized:** Bilateral posted-price exchange. At most one proposal and one acceptance/rejection message within the fixed deadline. The initial price is fixed before the run; no hidden second negotiation round. When the buyer rejects, flow is zero.

**Coordinated:** One dispatcher chooses flow under the same physical constraints. For an equivalent messaging comparison, the dispatcher must receive inputs through the same counted messages, or both policies must be given the complete shared inputs in advance. If the coordinator receives an uncounted privileged global state, the comparison is invalid.

**Baseline zero-gap control:** Price 40 units per input MWh, pumping 5, avoided boiler 80. Both select x=7.5; both system costs 37.5; protocol gap zero.

**Bounded-price failure fixture:** Price 80 units per input MWh, pumping 5, avoided boiler 80. The buyer rejects, decentralized flow 0, cost 600; centralized optimizer chooses x=7.5, cost 37.5. Gross protocol gap 562.5 units. **Interpretation:** This is an explicitly unfavorable fixed-price parameterization, not intrinsic superiority of central coordination. Report it as a protocol sensitivity, not the headline treatment effect.

**Price sweep and controls:** Preregister prices 0, 40, 74.99, 75, 80, 100; tie at buyer value = price + pumping resolves to no exchange. The zero-gap and failed-trade cases must both be reported. Vary communication rounds and deadline only after defining their effect on protocol state transitions. Do not claim a negotiation-round effect if no real update rule exists.

## Accounting
System operating cost excludes internal transfer payments, which cancel between nodes. Net protocol advantage = decentralized operating cost − coordinated operating cost − incremental protocol overhead. Report gross gap, overhead separately, total messages, message bytes, elapsed decision time (measured, not assumed), and any unmet load. If no empirical overhead exists, present break-even thresholds, not claimed net benefits.

## Stop/go gate
1. Add deterministic protocol-state implementation and tests for all price-sweep cases.
2. Ensure same physical evaluator and identical initial observations/permissions.
3. Demonstrate exact message accounting and zero-gap control.
4. Independent reviewer checks that any nonzero gap arises from specified price/round constraints, not unequal resources, hidden data or accounting errors.
5. Until these conditions pass, V3-A5 is a hypothesis/protocol, not validated evidence.
