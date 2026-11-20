# PSI-001 Gate-07 scientific and numerical audit

The six preserved synthetic runs reproduce byte for byte. The hand-calculated fixtures support the dispatch arithmetic for valid inputs. Two malformed-input fixtures expose validation failures. The flat-tariff comparison also fails to isolate a coordination effect because the planners receive different decision prices. With shared hourly prices, both use the same dispatch rule and the coordinated case costs 100,000 more in all three scenarios.

## Audit matrix

Line numbers refer to the preserved `psi001_annual.py`. Inspection identifies the implemented rules. Executed fixtures exercise those rules on independent, hand-calculated inputs. Saved-record checks compare existing results without rerunning the full year.

| Check | Result | Evidence and observation |
|---|---|---|
| Preserved source and results | PASS | Executed hash and byte checks. The source matched its Gate-05 digest. Both 4,959-byte JSON files were identical. Original, archive, and Gate-06 hashes were unchanged afterward. |
| Hourly electricity balance | PASS | Inspection, lines 45–48 and 57–61. Imports minus pump consumption plus unmet base electricity equals base load. Executed cap fixture: base load 90, pump draw 5, imports 95 MWh. Shortfall fixture: load 100, imports 95, unmet electricity 5 MWh. |
| Hourly heat balance and COP | PASS | Inspection, lines 6 and 47–62. Useful heat is pump electricity × 2.5 plus boiler heat; unmet heat closes the accounting identity. Executed cap fixture: pump electricity 5 yields useful heat 12.5, with 7.5 from the boiler versus demand of 20 MWh. The fixed COP models heat conversion without tracking ambient heat, delivery temperature, or efficiency variation. |
| Feasibility and dispatch | PASS | Inspection, lines 8–10 and 45–62. For valid nonnegative inputs, base electricity has priority. The pump is bounded by nameplate, spare import capacity, and heat demand. The boiler is bounded at 100 MWh. Over that interval the incremental cost slope is decision price − 45 × 2.5, so its sign selects a feasible endpoint after heat-service priority. Executed fixtures hit the 18 MWh pump cap, forced 8 MWh of pump use with heat demand 120 at an expensive hour, and selected the minimum pump at the exact 112.5 cost tie. |
| Cost components and reconciliation | PASS | Inspection, lines 7 and 64–79. Imports, including base electricity and pump draw, are charged at hourly price; boiler heat costs 45 per useful MWh. A's total equals dispatch cost, B's adds 100,000 once per run, and net savings are A minus B. Executed fixture: 95 × 40 + 7.5 × 45 = 4,137.5 for either planner, before overhead. All six saved totals, net savings, break-even values, and decision thresholds reconciled within 1e-8 absolute. The model excludes capital, fixed plant costs, fuel or emissions accounting beyond the boiler's aggregate marginal rate, distribution losses, and outage or unmet-service penalties. |
| Cold snap and outage implementation | PASS | Inspection and executed boundary fixtures, lines 41–49. Cold snap adds 30% to heat demand in hours 0–71; total heat was 1,892 MWh in the 73-hour fixture. Outage blocks the pump in hours 0–47; total pump use was 0 MWh over 48 hours and 10 MWh over 49 hours. The boiler and grid remain available under their usual limits. |
| Physical thermal-trunk resilience | INCONCLUSIVE | Inspection, lines 45–49 and 55–59. Pump unavailability is an equipment proxy. No trunk topology, delivery interruption downstream of both heat sources, or recovery dynamics were modeled. Zero unmet demand under this proxy establishes service only for the simulated case. |
| No-flexibility equivalence | PASS | Inspection and executed fixture, lines 45–55 and 69–72. At the import ceiling with different price signals, both used zero pump electricity and incurred 4,700 dispatch cost. B was 100,000 more expensive after overhead. |
| Shared-information equivalence | PASS | Inspection and executed flexible fixture, lines 53–55 and 87–93. Both receive the same hourly decision price and apply the same endpoint rule, so their hourly decisions agree for all valid inputs in this model. Fixture dispatch cost was 2,425 for each. The three saved shared-price records had zero pre-overhead savings. This equivalence follows from the model structure and cannot establish equivalence under storage, ramping, or network coupling. |
| Flat-tariff causal fairness | FAIL | Inspection and executed fixture, lines 11, 53–55, 64 and 87–88. A sees a flat 65 when choosing dispatch while B sees hourly price. Both are assessed at hourly prices and share physical bounds. At hourly price 130 the fixture gave A dispatch cost 2,600 and B 2,425. Giving A the same hourly price erased the 175-unit dispatch gap. The flat comparison measures the combined effect of different price signals and B's assumed overhead. |
| Unmet demand and service flags | PASS | Inspection, fixture, and saved records, lines 46–49 and 56–79. Overload fixture reported 5 MWh unmet electricity and 30 MWh unmet heat for each planner, with both flags false. All six annual records reported zero unmet heat and electricity and met service requirements. |
| Input validation | FAIL | Executed adverse fixtures, lines 36–49 and 57–62. Mismatched series lengths silently dropped an hour via zip and returned service_met=True. A negative base load produced a negative import and cost of −200 while passing the balance checks and service flag. The archived runs use internally generated, equal-length profiles, so these failures do not establish an error in the six saved records. |
| Numerical tolerances | PASS | Inspection and executed comparisons, lines 14, 60–62, 73–79, 84–85 and 91–94. Hourly assertions use absolute 1e-8 MWh, with strict inequality for balance residuals and inclusive import and service bounds. Service uses cumulative unmet demand. Annual input totals use math.isclose defaults (relative 1e-9, absolute 0). Float-sensitive fixture and saved cost arithmetic checks used absolute 1e-8 with no relative allowance. Gate-05 versus Gate-06 JSON used zero tolerance via byte equality. The favorable cost threshold uses a direct >= comparison. Python optimization mode can disable asserts. |
| Published 1% versus later draft 5% | PASS for published criterion, INCONCLUSIVE for draft provenance | Inspection, lines 13, 73 and 96–98, confirms 1% in code and saved metadata. The pinned public project map also says 1%. The stated later draft's 5% was tested as a counterfactual using archived net savings divided by A's total cost. No case passed either threshold. No source copy of the later draft was available in the inspected PSI-001 artifacts, so its date, authority, and intended scope could not be verified. |

## Commands and observed results

Run from the project workspace root on Windows 11 with CPython 3.15.2.

```powershell
py -I -S -B outputs/PSI-001-GATE-07/audit_fixtures.py
```

The fixture harness exited 0. Its two FAIL lines are confirmed model-input defects, which the harness treats as expected observations. It loaded the preserved source without invoking the annual entry point. [Fixture source](audit_fixtures.py) · [Complete observed output](fixture-output.log)

| Scenario | Flat net savings | Flat share of A cost | Hourly net savings | Hourly share of A cost |
|---|---:|---:|---:|---:|
| Baseline | 272,994.920768023 | 0.578387% | −100,000 | −0.213555% |
| Cold snap | 271,750.534337968 | 0.574772% | −100,000 | −0.213183% |
| Thermal-trunk outage | 268,045.120785087 | 0.567610% | −100,000 | −0.213423% |

Annual costs are synthetic currency units. The saved JSON contains annual aggregates, so this audit cannot independently compare archived per-hour dispatch schedules or residuals. Findings apply to the fixed-equipment, synthetic electricity and heating model.

[Published project map at the results commit](https://github.com/Open-Inquiry-Initiative/open-inquiry-initiative/blob/c1fc02174ac49e8d18bf3cf06dcfd16a161de178/PROJECTS.md#psi-001-synthetic-dispatch-experiment)
