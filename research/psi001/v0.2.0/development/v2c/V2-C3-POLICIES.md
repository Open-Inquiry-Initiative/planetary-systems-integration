# PSI-001 V2-C3 scheduling controls

**Coordination is unidentifiable in the C2 model.** C2 has one electricity import boundary, one heat bus and one storage state. Its common evaluator already enforces base-load priority, spare import capacity, equipment availability, heat service accounting and cyclic SOC. There is no modeled exchange agreement, reservation, or allocation decision that only a coordinated planner can make. A difference introduced by withholding a forecast, storage, or candidate schedules from one arm would change the experiment.

## Deterministic policy for each arm

The independent reference and the coordination-labeled control both use the same finite-menu scheduling policy. Both receive the same complete hourly profile and the same ordered menu of explicit candidate schedules. They have perfect foresight of demand, realized prices and availability within the supplied horizon. Both use the same immutable C2 plant, storage, equipment limits, initial and terminal SOC targets, and scoring function. There are no extra coordination actions.

Evaluate every candidate in the common C2 model. Discard infeasible schedules and fail explicitly if none remain. Rank feasible schedules lexicographically by total unmet electricity, total unmet heat, realized dispatch cost, and candidate position in the common menu. Lower is better for each measure. This is exact selection within the finite menu. It supplies no unrestricted optimizer and makes no claim that a candidate menu spans all physically possible schedules. The control returns the same immutable selection for both labels because their decision rights are identical.

Costs are C2 realized dispatch costs. The historic coordination overhead remains a separate assumed cost. This control does not charge either label differently or infer coordination savings. A future comparison needs an independently justified decision right and a resource-matched comparator before testing coordination. Access to storage and use of a different search algorithm must be kept separate from that decision right.

## Hand-worked controls

- Over two hours at prices 40 and 130, with electric loads 10 and 10 and heat loads 10 and 20, a no-shift candidate costs 2,760. Its heat-pump electricity is 4 MWh in hour one and its boiler supplies 20 MWh in hour two. A shift candidate uses 8 MWh of pump electricity in hour one, charges 10 MWh of heat, and discharges 10 MWh in hour two alongside 10 MWh of boiler heat. It costs 2,470 and ends at zero SOC. Both arms choose the shift when it is available to both. The 290 difference is between candidate schedules here.
- With zero storage capacity, both arms reject the shift and select the same no-shift schedule. A grid-capacity fixture also verifies that device actions cannot displace base-load priority.
- Feasibility, conservation, terminal state, shortfall priority and deterministic tie-breaking are checked in the fixture suite. No full-year experiment was run.
