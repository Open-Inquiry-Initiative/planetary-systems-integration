"""Isolated one-hour thermal storage. Energy quantities are MWh thermal.

Retention applies to opening SOC before charging or discharging. Charge
is heat supplied at the storage boundary and discharge is useful heat
returned at that boundary. Rate limits are MWh per one-hour interval.
"""
from dataclasses import dataclass
import math


ABS_TOL = 1e-9  # MWh thermal, for conservation and terminal SOC only


def nonnegative(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be finite and nonnegative")
    try:
        valid = math.isfinite(value) and value >= 0
    except OverflowError:
        valid = False
    if not valid:
        raise ValueError(f"{name} must be finite and nonnegative")


@dataclass(frozen=True)
class Storage:
    capacity: float
    charge_limit: float
    discharge_limit: float
    charge_efficiency: float = 1.0
    discharge_efficiency: float = 1.0
    retention: float = 1.0

    def __post_init__(self):
        for name in ("capacity", "charge_limit", "discharge_limit"):
            nonnegative(getattr(self, name), name)
        for name in ("charge_efficiency", "discharge_efficiency"):
            efficiency = getattr(self, name)
            nonnegative(efficiency, name)
            if not 0 < efficiency <= 1:
                raise ValueError(f"{name} must lie in (0, 1]")
        nonnegative(self.retention, "retention")
        if self.retention > 1:
            raise ValueError("retention must lie in [0, 1]")


@dataclass(frozen=True)
class Transition:
    opening_soc: float
    charge: float
    discharge: float
    retention_loss: float
    charge_loss: float
    discharge_loss: float
    closing_soc: float
    balance_residual: float


def check_soc(storage, soc):
    nonnegative(soc, "SOC")
    if soc > storage.capacity:
        raise ValueError("SOC exceeds storage capacity")


def step(storage, soc, *, charge, discharge):
    """Apply one feasible hour, with no clipping or implicit heat supply."""
    check_soc(storage, soc)
    nonnegative(charge, "charge")
    nonnegative(discharge, "discharge")
    if charge > storage.charge_limit or discharge > storage.discharge_limit:
        raise ValueError("charge or discharge exceeds its rate limit")
    if charge > 0 and discharge > 0:
        raise ValueError("simultaneous charge and discharge is prohibited")
    if storage.capacity == 0 and (charge > 0 or discharge > 0):
        raise ValueError("zero-capacity storage cannot transfer heat")

    retained = soc * storage.retention
    stored_charge = charge * storage.charge_efficiency
    withdrawal = discharge / storage.discharge_efficiency
    if not math.isfinite(withdrawal) or withdrawal > retained:
        raise ValueError("discharge exceeds available SOC after retention")
    closing_soc = retained - withdrawal + stored_charge
    check_soc(storage, closing_soc)

    retention_loss = soc - retained
    charge_loss = charge - stored_charge
    discharge_loss = withdrawal - discharge
    # Storage boundary: opening SOC + heat in = closing SOC + useful heat out + losses.
    residual = math.fsum((soc, charge, -closing_soc, -discharge,
                          -retention_loss, -charge_loss, -discharge_loss))
    if not math.isclose(residual, 0, rel_tol=0, abs_tol=ABS_TOL):
        raise ArithmeticError(f"storage energy balance residual {residual:g} MWh")
    return Transition(soc, charge, discharge, retention_loss, charge_loss,
                      discharge_loss, closing_soc, residual)


def run_schedule(storage, flows, *, initial_soc=0.0):
    """Apply (charge, discharge) pairs and require terminal SOC = initial SOC."""
    check_soc(storage, initial_soc)
    transitions = []
    soc = initial_soc
    for charge, discharge in flows:
        transition = step(storage, soc, charge=charge, discharge=discharge)
        transitions.append(transition)
        soc = transition.closing_soc
    if not math.isclose(soc, initial_soc, rel_tol=0, abs_tol=ABS_TOL):
        raise ValueError("terminal SOC must equal initial SOC")
    return tuple(transitions)
