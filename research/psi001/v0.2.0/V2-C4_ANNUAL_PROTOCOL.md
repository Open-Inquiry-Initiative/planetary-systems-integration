# PSI-001 V2-C4 — Annual evaluation protocol and identifiability boundary

**Status:** Preregistered protocol only; no annual V2-C results in this document.
**Input baseline:** V2-C3 commit `5097736bfba88bc212605bc38bf7cf815ab1267b`.
**Finding entering C4:** C2/C3 contain no coordination-exclusive decision; coordinated and independent policies use identical information, feasible candidates and deterministic selection. A coordination effect is **not identifiable** in this model.

## Questions
1. Does the existing thermal-storage schedule selection remain feasible and reproducible when applied to annual synthetic inputs?
2. What is the economic value of allowing a storage schedule versus a no-storage/no-shift schedule, holding information and equipment assumptions explicit?
3. Do paired equal-resource policies continue to produce identical dispatch before overhead? This is an equivalence/negative control, **not** a measured coordination effect.

## Preregistered design
- Run baseline, cold snap and heat-pump outage **proxy** under unchanged versioned synthetic inputs; clearly identify any modifications needed to generate storage-feasible candidate schedules.
- Compare no-storage and storage-enabled scheduling with common realized hourly prices, heat demand, COP, outage assumptions and constraints. Report this as a **flexibility/resource** comparison, not coordination.
- Evaluate independent and coordinated-control policies with identical storage access, candidate schedules, information and selection rules; expected pre-overhead difference is zero by construction. Report assumed overhead separately (historical 100,000 synthetic currency units), and never describe net difference as a measured coordination effect.
- Include zero-capacity, zero-charge-rate, flat-price and no-flexibility negative controls where feasible. Reject or explicitly report infeasible schedules; do not silently inject backup supply.
- Require the same initial and terminal SOC, hourly conservation residuals within the established 1e-9 MWh tolerance, capacity/rate/availability constraints and no simultaneous charge/discharge.
- Do not treat deterministic three-scenario outputs as statistical significance or physical network resilience.

## Reporting
Primary *descriptive* outcomes: paired annual realized dispatch cost difference for storage vs no-storage, unmet heat/electric MWh, constraint violations and hourly conservation residuals. Report overhead-adjusted control contrasts separately with explicit non-identifiability caveat. Secondary: storage throughput, SOC range, conversion/retention losses, heat-pump electricity, fuel use, and terminal SOC.
Archive hourly inputs and schedules, all dispatch traces, assumptions, config, exact commands, interpreter version, test logs and SHA-256 manifest. Preserve all null/negative findings. If annual schedules cannot be defined under existing C2/C3 policy rules, stop and document the gap rather than inventing an optimizer after seeing results.

## Execution gates
1. Confirm annual schedule-generation rules are fixed before evaluation and are not tuned on results.
2. Pass 38 prior tests plus new annual consistency, feasibility and replay checks.
3. Independently rerun and compare bytes/hashes or explain nondeterminism.
4. Audit attribution: storage/flexibility effect versus unidentifiable coordination effect.
5. Keep PR #9 draft and v0.1.0 immutable; no merge or release without separate review.

## Next distinct scientific mechanism (future, not part of C4)
A coordination-specific decision would require explicit interacting actors/resources (for example two independently constrained heat producers and a shared network/storage transfer constraint) and a genuine decentralized-versus-joint feasible-decision distinction. Such a model requires its own preregistration and controls; it must not be retroactively added to C4.
