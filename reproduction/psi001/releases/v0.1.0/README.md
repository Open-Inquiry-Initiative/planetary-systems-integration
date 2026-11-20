# PSI-001 v0.1.0 Reproduced Synthetic Experiment

Local release candidate assembled on November 19, 2026. The experiment compares independent and coordinated electricity and district-heating dispatch over one synthetic year with fixed equipment.

| Scenario | Flat tariff net savings | Shared hourly price net savings |
|---|---:|---:|
| Baseline | 272,995 | −100,000 |
| 72-hour cold snap | 271,751 | −100,000 |
| 48-hour outage proxy | 268,045 | −100,000 |

Figures are rounded synthetic currency units. They include 100,000 units of assumed annual overhead for coordination. Both planners report zero unmet electricity and heat demand across all six records. The isolated Gate-06 rerun reproduced the archived JSON byte for byte.

## Adverse findings and limits

- No scenario met the published 1% net savings threshold. Applying the stated later 5% threshold to the saved values also yields no favorable scenarios. The later draft and its authority were unavailable for verification. The archived experiment retains its original 1% criterion.
- The flat-tariff case gives the planners different decision prices. Its savings cannot be attributed to coordination alone. With the same hourly decision prices, both planners use the same dispatch rule and dispatch costs match. Coordination adds only its assumed overhead.
- The simulated thermal-trunk outage disables the heat pump for 48 hours while leaving the boiler and grid available. Physical heat delivery, network failure, and recovery were outside the model.
- The model silently truncates unequal-length series and accepts negative base load. An executed negative-load fixture returned a dispatch cost of −200 and service_met=True. The archived runs used equal-length, internally generated inputs. These validation failures remain in the preserved code.
- Model scope is fixed equipment and independent hourly intervals. It excludes storage, ramping, network topology, distribution losses, capital costs, and outage or unmet-service penalties. Hourly inputs are generated in memory. The archived results are annual aggregates, so hourly schedules and residuals cannot be compared directly from those files.

## Evidence and integrity

- [Gate-05 provenance and embedded configuration](PSI-001-GATE-05/PROVENANCE.md) and [sanitized original execution excerpt](PSI-001-GATE-05/execution-excerpt.txt)
- [Gate-06 reproduction report](PSI-001-GATE-06/REPRODUCTION.md), [execution metadata](PSI-001-GATE-06/execution.json), [complete stdout](PSI-001-GATE-06/annual-rerun.json), and [complete stderr](PSI-001-GATE-06/stderr.log)
- [Gate-07 audit matrix](PSI-001-GATE-07/AUDIT.md), [fixture source](PSI-001-GATE-07/audit_fixtures.py), and [complete fixture output](PSI-001-GATE-07/fixture-output.log)
- [Release inventory](INVENTORY.md), [SHA-256 manifest](SHA256SUMS.txt), and [readiness report](READINESS.md)

The release manifest covers every other file in this directory. Entries are relative to the release-candidate root. Gate-05 retains its original four-file manifest. The included Gate-05 ZIP is the verified preservation archive used by the unmodified audit harness.

The preserved logs document earlier execution. For a future reproduction, the Gate-06 command is recorded in its execution metadata. The Gate-07 command below is relative to this release-candidate root.

```powershell
py -I -S -B PSI-001-GATE-07/audit_fixtures.py
```
