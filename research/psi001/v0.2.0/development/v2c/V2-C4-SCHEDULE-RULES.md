# V2-C4 fixed annual schedule rules

These implementation rules are committed before running any C4 comparisons.
They refine the finite-menu design in the annual protocol. Both labels use the
same realized prices and full inputs with no coordination-exclusive decision.
**Coordination is unidentifiable.**

- Start with the unchanged V2-A synthetic profiles. Apply the original first
  72-hour 30% heat-load increase or the original first 48-hour heat-pump
  unavailability, in separate scenarios. No grid or thermal network outage is
  implied. All schedules start and end with 0 MWh thermal SOC.
- The no-shift candidate serves base electricity first, then maximizes heat
  service under the C2 bounds. It uses the heat pump before the boiler when
  hourly price < boiler cost × COP. Otherwise it uses the boiler first. Boiler
  output is adjusted upward by at most 1e-12 MWh, within its limit, when a
  nominally fully served hour would otherwise round below heat demand.
- The storage-enabled menu includes no-shift first, then one adjacent-pair
  candidate. Use disjoint pairs (hours 0–1, 2–3, and so on). If the first hour
  has spare heat-pump and import capacity and can charge, it may charge from
  additional heat-pump output to displace the second hour's no-shift boiler
  heat. Require both hours' storage availability and a strict realized
  marginal cost advantage after losses. Charge in whole MWh thermal, taking
  the largest amount bounded by spare pump supply, storage capacity, charge
  limit, next-hour discharge limit and removable boiler heat. Discharge all
  resulting retained energy in the second hour. A final unpaired hour keeps
  its no-shift dispatch. No extra supply or heat dumping is introduced.
- For the storage arm use 16 MWh SOC capacity, 8 MWh/hour charge and discharge
  limits, and 0.875 for each efficiency and hourly retention. These are fixed
  synthetic parameters. Main equipment limits use C2 defaults. The
  no-storage reference has zero storage capacity and rates. Negative controls
  set storage capacity to zero, charge rate to zero, prices to a common 65,
  or pump capacity to zero (eliminating the defined charge mechanism).
- Use C3's shared lexicographic selector without changing its service
  priorities or tie-break. Report rejected candidates and fail if the
  reference schedule cannot be replayed. Audit each selected trace. Report
  the 100,000-unit assumed overhead separately from the zero pre-overhead
  label contrast. No fit or annual optimum is claimed.
- Replay the main arms and applicable negative controls over all three
  scenarios and rerun the export in a new process. Numerical heat/electric
  balance and cyclic terminal comparisons use absolute 1e-9 MWh tolerance.
  Export machine-readable hourly inputs, selected schedules, results and
  losses. Boiler useful-heat output is reported; no fuel conversion factor
  was specified, so fuel use in input-energy units is unavailable.