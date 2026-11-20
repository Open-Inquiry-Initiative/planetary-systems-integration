# PSI-001 Gate-06 reproduction report

**Result.** The isolated rerun exited with code 0. Its complete stdout is byte-for-byte identical to the archived annual JSON. Complete stderr is empty (0 bytes). All six records and every serialized field matched exactly. Numeric comparisons used absolute tolerance 0 and relative tolerance 0. The original model's internal balance and service tolerance remains 1e-8.

## Integrity and environment

The four Gate-05 manifest hashes matched the files in the original output directory, the preservation directory, and the Gate-05 ZIP before execution. The copied annual source matched the manifest before execution. After the run, the original and preservation-directory hashes still matched, and the Gate-05 ZIP retained its recorded SHA-256.

- Annual source SHA-256: `4f9e2113b4e9a641dd04987d2dc801b6b34a8505d4eb24715795e03a5611a03a`
- Archived and rerun JSON SHA-256: `d2cf48d7714606b882fe49216ab6342af5224c3b0991727e51f7d6120a935add`
- Interpreter: CPython 3.15.2, 64-bit AMD64 on Windows 11 (build 26200).
- Dependencies: Python standard library modules `json` and `math`. No third-party packages.
- Command: `python -I -S -B psi001_annual.py` from the fresh Gate-06 directory, using the resolved CPython interpreter. The flags enable isolated mode, skip site initialization, and disable bytecode writes.
- Run window: 2026-11-19 23:54:04.775 to 23:54:05.014 UTC. See [execution metadata](execution.json), [complete stdout](annual-rerun.json), and [complete stderr](stderr.log).

## Exact differences

Each difference is rerun minus archive. Cost columns cover dispatch and total cost for both planners. Unmet demand covers both electricity and heat for both planners. All costs are in synthetic currency units and demand is in MWh.

| Tariff | Scenario | Independent cost Δ | Coordinated cost Δ | Net savings Δ | Unmet demand Δ | Saved net savings, rounded |
|---|---|---:|---:|---:|---:|---:|
| flat_tariff | baseline | 0 | 0 | 0 | 0 | 272995 |
| flat_tariff | cold_snap | 0 | 0 | 0 | 0 | 271751 |
| flat_tariff | thermal_trunk_outage | 0 | 0 | 0 | 0 | 268045 |
| hourly_tariff | baseline | 0 | 0 | 0 | 0 | -100000 |
| hourly_tariff | cold_snap | 0 | 0 | 0 | 0 | -100000 |
| hourly_tariff | thermal_trunk_outage | 0 | 0 | 0 | 0 | -100000 |

Both planners again report zero unmet demand in every scenario. No scenario meets the 1% savings threshold. The reproduction covers the preserved synthetic model and this execution environment.
