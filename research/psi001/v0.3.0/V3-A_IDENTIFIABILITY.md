# PSI-001 v0.3.0 — V3-A coordination identifiability preregistration

**Status:** Analytical fixture and falsification specification; not a simulated or field-tested result.
**Prerequisite:** v0.3.0 roadmap. Both arms use identical forecasts, costs, equipment and constraints. The only treatment difference is permission to transfer heat between nodes.

## Hand-worked two-node fixture (one hour)
- Node A has 10 MWh of otherwise-curtailed usable heat at 80°C; local demand 0 MWh.
- Node B requires 6 MWh of useful heat at 60°C. Its backup boiler can meet demand at 100 synthetic currency units per MWh delivered.
- A-to-B thermal link can carry up to 8 MWh input per hour, with 20% thermal loss. Pumping/transport costs 5 synthetic currency units per MWh input. Heat transfer from 80°C to a 60°C sink is thermodynamically permitted in this simplified fixture; temperature compatibility is an explicit model constraint.
- No storage, no electricity conversion, no other demand or generation. Unused heat is curtailed without credit. Both arms know all inputs and have the same boiler and link hardware; only their dispatch policy differs.

**Independent policy:** No inter-node transfer (link held closed). B uses 6 MWh boiler heat. Total operating cost = 6 × 100 = **600** units. A curtails 10 MWh.

**Coordinated policy:** Transfer 7.5 MWh from A; deliver 7.5 × 0.8 = 6 MWh to B; pump cost = 7.5 × 5 = **37.5** units; boiler use = 0; A curtails 2.5 MWh. Link 7.5 ≤ 8 MWh. Heat balance: 7.5 input = 6 delivered + 1.5 lost. B demand 6 = 6 transferred + 0 boiler. Total cost = **37.5** units.

**Gross coordination savings** = 600 − 37.5 = **562.5 synthetic units** in this fixture. Net coordination value = 562.5 − incremental coordination overhead (unknown, must be explicitly specified). Break-even overhead = 562.5 units per fixture-hour.

## Identifiability caveat
This is a **policy-access comparison**, not proof of a benefit from centralized intelligence or communication alone. Since independent dispatch is defined as link-closed, the observed difference is the value of *permitting and using inter-node heat exchange* under the specified fixture. A fairer follow-up must compare decentralized market-based exchange versus centralized coordinated exchange with both arms allowed to use the same link, information and feasible actions. If both optimize the same objective and constraints perfectly, coordination-specific advantage may be zero. Report these estimands separately:
1. **Network exchange value:** no-exchange versus exchange-allowed.
2. **Coordination mechanism value:** independent/decentralized versus coordinated policy with the same exchange rights, network, information and resources.
Do not label (1) as (2).

## Falsification and negative controls
- **Zero link capacity:** both arms must use boiler for 6 MWh; savings = 0.
- **Zero available A heat:** savings = 0.
- **Pumping cost 100 units/MWh input:** exchange is more expensive than boiler; optimal exchange = 0 and savings = 0.
- **Incompatible source temperature:** if 80°C source cannot serve the sink due to imposed approach/quality constraints, exchange forbidden; savings = 0.
- **Equal exchange rights and identical optimal policies:** coordination-mechanism value = 0, even though network exchange value may remain positive.
- **Accounting test:** reject negative flow, flow > 8, heat delivered > 0.8 × flow, or unmet B demand without explicit penalty/accounting.

## V3-A acceptance criteria
1. Reproduce all fixture calculations by hand and a minimal deterministic unit test.
2. Specify exactly which policy permissions differ and which do not.
3. Demonstrate at least one distinct *mechanism* between decentralized and coordinated arms **without changing rights or information**; otherwise classify coordination-mechanism benefit **unidentifiable** and stop before V3-B.
4. Preregister overhead assumptions, solver/tie-breaking and controls before any multi-hour or annual comparison.
5. Independent reviewer checks units, conservation and counterfactual interpretation.

**Current V3-A outcome:** Network exchange value is analytically identifiable in this constructed fixture. The stronger coordination-mechanism effect is **not yet identified**. This document is a preregistration/illustration, not a passed V3-A gate.
