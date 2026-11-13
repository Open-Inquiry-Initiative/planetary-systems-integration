# PSI-001 — Initial experiment protocol (draft)

## Objective
Test whether multi-layer coordination can improve specified combinations of energy, resource consumption, resilience and human service delivery compared with independent subsystem planning.

## Reference system (synthetic, not observed)
- 100,000 residents; 100 km².
- 500 GWh/year electricity demand and 300 GWh/year useful heating demand.
- Time step: hourly; initial evaluation horizon: one synthetic year.
- These are **chosen test parameters**, not city statistics or measured forecasts.

## Model A: independent optimization
Electricity, heating, water and transportation optimize locally while satisfying shared minimum service constraints. Exchange occurs through explicit interfaces, but no cross-sector optimization objective is permitted.

## Model B: coordinated optimization
The same equipment choices, technology capabilities, demand, constraints and budgets apply; scheduling and siting decisions can coordinate across sectors. Account for coordination overhead, communications failures and additional capital expense.

## Accounting requirements
- Enforce energy balance at each node and across the system.
- Track temperature and exergy of thermal streams; heat pumps consume external work.
- Do not count refrigerator condenser heat or recovered heat as newly created energy.
- Model spatial and hourly coincidence of sources and demand, distribution losses, storage losses and peak capacities.
- Compare lifecycle costs, not only operational energy.
- Define explicit minimum service and welfare constraints before optimizing.

## Scenarios
Baseline climate; cold snap; heat wave; drought; loss of thermal trunk; grid islanding; communications disruption; erroneous sensor inputs.

## Outputs
Per-sector and total electricity/heat/fuel, water withdrawals, material throughput, emissions, unserved demand, costs, fault recovery and Pareto frontiers. Report uncertainty and sensitivity to input assumptions.

## Falsification and stopping rules
If B fails to outperform A on any meaningful trade-off after accounting for complexity and costs, record that result. Reject configurations that violate physical balances, safety limits or human-service minima. Preserve input files, code versions, seeds, decision logs and negative results.

## Not yet done
No code, calibrated datasets, empirical tests, external peer review or verified savings estimates are supplied in this release.
