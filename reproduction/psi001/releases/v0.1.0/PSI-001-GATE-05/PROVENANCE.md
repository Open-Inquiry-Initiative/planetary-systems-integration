# PSI-001 Gate-05 preservation package

The four original files are byte-for-byte copies of the locally saved PSI-001 pilot and annual simulation artifacts. The pilot predates the annual run. The original annual execution was captured on November 19, 2026 at 22:14:19 UTC. Only its six scenario lines and basic execution metadata are included here. The results were later summarized in [public project-map commit c1fc021](https://github.com/Open-Inquiry-Initiative/open-inquiry-initiative/commit/c1fc02174ac49e8d18bf3cf06dcfd16a161de178).

## Embedded annual configuration

- 8,760 one-hour intervals in a synthetic 365-day year. The model generates the profiles deterministically in memory using the Python standard library.
- Seasonal factor is cos(2π × day / 365). Evening peak applies from hour 17 through hour 21. Electricity is shaped by 60 + 8 × seasonal factor + 15 × peak indicator, then normalized to 500,000 MWh. Temperature is 12 − 11 × seasonal factor. Heating uses max(0, 18 − temperature), normalized to 300,000 MWh before scenario adjustments.
- Hourly electricity price is 55 + 15 × seasonal factor + 70 × peak indicator. Independent dispatch uses either a flat decision tariff of 65 or the hourly price. Coordinated dispatch uses the hourly price. Both models account for imported electricity at the hourly price.
- Heat pump COP is 2.5. Pump electricity is capped at 18 MWh per interval. Imported electricity is capped at 95 MWh per interval. The boiler supplies up to 100 MWh of useful heat per interval at 45 synthetic currency units per MWh.
- Base electric demand is served before allocating spare import capacity to the heat pump. Both dispatch rules use the same feasible bounds. Their decision prices determine which hourly endpoint they choose, with a switch at the boiler cost times COP. Equipment is fixed. The model has no storage or ramping constraints.
- The cold snap increases useful heating demand by 30% during the first 72 hours. The simulated thermal-trunk outage disables the heat pump during the first 48 hours. Each disruption is tested separately from the other.
- Coordinated dispatch carries a fixed annual cost of 100,000 synthetic currency units. A favorable case must meet service requirements and save at least 1% of independent total cost. The balance and service tolerance is 1e-8.

## Verification of saved results

Net savings were recomputed from the saved cost fields, and rounded values were compared with the published figures. Across all six records, both models report zero unmet electricity and heat demand, and no case meets the 1% threshold. The preserved JSON contains annual summaries. The original hourly inputs were generated in memory, and no hourly dispatch export was identified. This verification did not rerun either simulation.

| Tariff | Scenario | Saved net savings | Rounded | Published |
|---|---|---:|---:|---:|
| flat_tariff | baseline | 272994.920768023 | 272995 | 272995 |
| flat_tariff | cold_snap | 271750.534337968 | 271751 | 271751 |
| flat_tariff | thermal_trunk_outage | 268045.120785087 | 268045 | 268045 |
| hourly_tariff | baseline | -100000 | -100000 | -100000 |
| hourly_tariff | cold_snap | -100000 | -100000 | -100000 |
| hourly_tariff | thermal_trunk_outage | -100000 | -100000 | -100000 |
