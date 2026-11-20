# PSI-001 V2-D independent audit of annual storage results

**Finding:** The repeated storage savings are explained by the scenario timing. The audited hour-by-hour saving is 6,077.81602571103 synthetic currency units in each main case. Storage moved heat on the same 196 hours in all three scenarios. None of those hours overlap a scenario-specific input change. **Coordination remains unidentifiable.**

## Why the three results agree

Hours below are zero-based. Versus baseline, only heat load changed in the cold snap (hours 0–71), and only heat-pump availability changed in the outage proxy (hours 0–47). Prices and base electric demand did not change. The first storage move was at hour 1,816 and the last was at 6,977. Storage operated on 98 adjacent pairs, charging at hour-of-day 16 and discharging at hour-of-day 17. The 98 charging prices ranged from 47.20 to 59.14, and the discharge-hour prices ranged from 117.20 to 129.14. At discharge, the supplied heat displaces boiler output. All 196 active records and their paired hourly cost differences were identical across scenarios. The paired hourly cost difference was zero outside those hours. Scenario-specific costs moved together between the two arms, so they canceled in the flexibility contrast.

The sum of hourly differences and the C4 subtraction of annual totals differ by approximately 5.7e-10 currency units. They agree at reported precision. These traces do not measure the value of storage during the cold snap or outage itself.

## Archived trace verification

The audit parsed all 131,400 exported hours across 15 cases, checking both recorded arms (262,800 arm-hours). It independently reconstructed imports, COP heat, delivery, storage losses, unmet demand, and realized costs from inputs and dispatch instructions. It checked equipment availability, capacity, rates, no simultaneous transfers, no hidden heat, SOC continuity, and the common initial and terminal SOC of zero. It reconciled each annual aggregation. Hourly comparisons used absolute 1e-9 and relative zero. The largest observed deviation was 9.99200722162641e-13. The existing no-flexibility cold-snap control independently reproduced 543.077958068264 MWh of unmet heat. All 17 files in each of the original and replay exports matched the pinned manifest. These checks read the saved files and do not call the C2 evaluator.

## Exploratory sensitivity results

These runs use the unchanged C4 finite menu and vary the named parameter or tariff. The lossless-conversion case jointly changes both conversion efficiencies and retains the original hourly retention. The half-premium tariff reduces the 70-unit evening premium to 35 for both dispatch and scoring. All three scenarios agree to the displayed precision. The largest tiny difference across scenarios in these sensitivity results is below 1e-8 currency units. No candidate was rejected.

| Exploratory case | Flexibility savings, synthetic currency units |
|---|---:|
| Frozen C4 reference | 6,077.82 |
| Capacity 4 / 32 MWh | 3,310.86 / 6,077.82 |
| Charge efficiency 0.5 / discharge efficiency 0.5 | 0 / 0 |
| Both conversion efficiencies 1.0 | 11,974.63 |
| Hourly retention 0.5 / 1.0 | 0 / 8,796.33 |
| Charge limit 4 / 12 MWh per hour | 3,310.86 / 7,807.08 |
| Discharge limit 2 / 12 MWh per hour | 1,722.38 / 6,077.82 |
| Flat tariff 65 / half evening premium | 0 / 0 |

The frozen schedule peaks at 7 MWh SOC, so expanding capacity from 16 to 32 does not create new opportunities under these rules. The tariff sensitivities change the realized cost of the same resource comparison. Zero values mean the shared menu selected no beneficial shift under those settings. They do not establish a universal break-even tariff.

Separate overhead accounting left the identical-label pre-overhead difference at zero. Assumed overheads of 0, 5,000, 10,000 and 100,000 yield label differences of 0, −5,000, −10,000 and −100,000. These are arithmetic consequences of the assumptions and do not change the storage-flexibility estimates.

## Reproduction and limits

From the repository root, supplying the two original export directories as arguments:

```powershell
py -I -S -B -m unittest discover -s research/psi001/v0.2.0/development -v
py -I -S -B -m unittest discover -s research/psi001/v0.2.0/development/v2c -v
py -E -S -B research/psi001/v0.2.0/development/v2c/audit_annual_storage.py ORIGINAL_EXPORT INDEPENDENT_REPLAY NEW_AUDIT_JSON
```

All 46 tests passed on CPython 3.15.2 on Windows 11. The audit exited zero with empty stderr. The JSON captures the active-hour records, changed-hour indices, full scenario sensitivity results, and environment. Audit JSON SHA-256: `06379b53fc8ee9142c8783662c30d90a4f4f96688de8b01f1dcbb911c657ef98`.

The sensitivity analysis is exploratory, uses the same limited adjacent-pair candidate family, and omits storage investment cost. It establishes neither an annual optimum nor physical network resilience. A different synthetic price profile, disruption window or scheduling policy may alter the storage result. An identifiable coordination comparison would need a coordination-exclusive modeled decision under equal resources and information.
