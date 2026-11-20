# PSI-001 V2-C4 annual replay results

The schedule rules were fixed in commit b8eabeb1b006e0bf5b5be5989358b9cc29152a4e before any comparison ran. Both labels use the same candidate menu and evaluation. **Coordination is unidentifiable.**

| Scenario | No-storage dispatch cost | Storage-enabled dispatch cost | Flexibility savings |
|---|---:|---:|---:|
| Baseline | 46,826,344.82 | 46,820,267.01 | 6,077.82 |
| Cold snap | 46,907,998.09 | 46,901,920.28 | 6,077.82 |
| Heat-pump outage proxy | 46,855,415.58 | 46,849,337.77 | 6,077.82 |

Amounts are synthetic currency units. In each main case, the finite-menu storage schedule charged 674 MWh thermal and returned 451.52734375 MWh thermal. Losses were 84.25 MWh during charging, 73.71875 during retention, and 64.50390625 during discharge. Peak SOC was 7 MWh and terminal SOC was zero. Both arms met all demand. The main-case maximum absolute balance residual was below 1e-12 MWh. No shift candidate was rejected in the 15 exported cases.

All 12 negative-control cases had zero flexibility savings. During the cold snap with heat-pump capacity set to zero, both arms had 543.077958068264 MWh of unmet heat. The evaluator recorded that shortfall without adding supply. The equal-resource label contrast is zero before overhead in every case. Subtracting the separately assumed 100,000-unit overhead produces −100,000 mechanically, with no identified coordination effect. The outage proxy disables the heat pump for the first 48 hours. Fuel input was unavailable because the model specifies only boiler useful heat.

Run these commands from the repository root in CPython 3.15.2 on Windows 11. The output directory must be new on each execution.

```powershell
py -I -S -B -m unittest discover -s research/psi001/v0.2.0/development -v
py -I -S -B -m unittest discover -s research/psi001/v0.2.0/development/v2c -v
py -E -S -B research/psi001/v0.2.0/development/v2c/annual_storage.py annual
py -E -S -B research/psi001/v0.2.0/development/v2c/annual_storage.py independent-replay
```

All 42 tests passed. The two independent process outputs had matching SHA-256 digests across 15 compressed hourly traces, the summary, and the environment record. Each trace contains inputs, schedules, and C2 results for the reference and identical-resource control. The baseline test also decodes and replays both exported traces through C2. Manifest SHA-256: `828ab7f7d376f8484857d57fbb0906f3d2ffc56324c74bfb5b67867aad5d5a23`.

These results describe one fixed adjacent-pair schedule rule over three synthetic scenarios. They provide no estimate of an annual optimum or physical network resilience.
