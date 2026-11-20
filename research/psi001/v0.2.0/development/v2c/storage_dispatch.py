"""Evaluate explicit hourly schedules under a common physical resource model.

This module evaluates schedules from either planner. It does not choose
dispatch or add coordination overhead. Heat is in MWh thermal, electricity
is in MWh electric, and prices and costs use synthetic currency units.
"""
from dataclasses import dataclass
import math

from thermal_storage import ABS_TOL, Storage, Transition, check_soc, nonnegative, step


@dataclass(frozen=True)
class Plant:
    storage: Storage
    import_limit: float = 95
    pump_limit: float = 18  # electric input
    cop: float = 2.5
    boiler_limit: float = 100  # useful heat output
    boiler_cost: float = 45  # per MWh of useful heat

    def __post_init__(self):
        for name in ("import_limit", "pump_limit", "cop", "boiler_limit", "boiler_cost"):
            nonnegative(getattr(self, name), name)
        if self.cop == 0:
            raise ValueError("COP must be positive")


@dataclass(frozen=True)
class Hour:
    electric_load: float
    heat_load: float
    price: float
    grid_available: bool = True
    pump_available: bool = True
    boiler_available: bool = True
    storage_available: bool = True

    def __post_init__(self):
        nonnegative(self.electric_load, "electric load")
        nonnegative(self.heat_load, "heat load")
        # Negative realized market prices are allowed, as in V2-A.
        if isinstance(self.price, bool) or not isinstance(self.price, (int, float)):
            raise ValueError("price must be finite")
        try:
            finite_price = math.isfinite(self.price)
        except OverflowError:
            finite_price = False
        if not finite_price:
            raise ValueError("price must be finite")
        for name in ("grid_available", "pump_available", "boiler_available", "storage_available"):
            if type(getattr(self, name)) is not bool:
                raise ValueError(f"{name} must be boolean")


@dataclass(frozen=True)
class Dispatch:
    pump_electricity: float
    boiler_heat: float
    charge: float = 0
    discharge: float = 0

    def __post_init__(self):
        for name in ("pump_electricity", "boiler_heat", "charge", "discharge"):
            nonnegative(getattr(self, name), name)


@dataclass(frozen=True)
class HourResult:
    storage: Transition
    pump_electricity: float
    pump_heat: float
    boiler_heat: float
    heat_produced: float
    heat_delivered: float
    electricity_purchased: float
    base_electricity_served: float
    electricity_cost: float
    boiler_cost: float
    realized_cost: float
    unmet_electricity: float
    unmet_heat: float
    electricity_balance_residual: float
    heat_balance_residual: float


def evaluate_hour(plant, hour, dispatch, soc):
    """Score one hour. Base electricity has priority over pump electricity."""
    import_limit = plant.import_limit if hour.grid_available else 0
    pump_limit = plant.pump_limit if hour.pump_available else 0
    boiler_limit = plant.boiler_limit if hour.boiler_available else 0
    served = min(hour.electric_load, import_limit)
    if dispatch.pump_electricity > min(pump_limit, import_limit - served):
        raise ValueError("pump electricity exceeds available pump or import capacity")
    if dispatch.boiler_heat > boiler_limit:
        raise ValueError("boiler heat exceeds available boiler capacity")
    if not hour.storage_available and (dispatch.charge or dispatch.discharge):
        raise ValueError("storage is unavailable")

    storage = step(plant.storage, soc, charge=dispatch.charge, discharge=dispatch.discharge)
    pump_heat = dispatch.pump_electricity * plant.cop
    heat_produced = pump_heat + dispatch.boiler_heat
    nonnegative(heat_produced, "heat production")
    if storage.charge > heat_produced:
        raise ValueError("storage charge exceeds heat production")
    heat_supply = heat_produced - storage.charge + storage.discharge
    nonnegative(heat_supply, "heat supply")
    if heat_supply - hour.heat_load > ABS_TOL:
        raise ValueError("heat supply exceeds demand; heat dumping is not modeled")
    heat_delivered = min(heat_supply, hour.heat_load)
    unmet_heat = hour.heat_load - heat_delivered
    purchased = served + dispatch.pump_electricity
    unmet_electricity = hour.electric_load - served
    electricity_cost = purchased * hour.price
    boiler_cost = dispatch.boiler_heat * plant.boiler_cost
    realized_cost = electricity_cost + boiler_cost
    if not all(math.isfinite(value) for value in (electricity_cost, boiler_cost, realized_cost)):
        raise ValueError("realized costs must be finite")

    electricity_residual = math.fsum((purchased, -served, -dispatch.pump_electricity))
    heat_residual = math.fsum((heat_produced, storage.discharge, -storage.charge, -heat_delivered))
    if abs(electricity_residual) > ABS_TOL or abs(heat_residual) > ABS_TOL:
        raise ArithmeticError("hourly electricity or heat balance does not close")

    return HourResult(
        storage=storage,
        pump_electricity=dispatch.pump_electricity,
        pump_heat=pump_heat,
        boiler_heat=dispatch.boiler_heat,
        heat_produced=heat_produced,
        heat_delivered=heat_delivered,
        electricity_purchased=purchased,
        base_electricity_served=served,
        electricity_cost=electricity_cost,
        boiler_cost=boiler_cost,
        realized_cost=realized_cost,
        unmet_electricity=unmet_electricity,
        unmet_heat=unmet_heat,
        electricity_balance_residual=electricity_residual,
        heat_balance_residual=heat_residual,
    )


def evaluate_schedule(plant, hours, dispatches, *, initial_soc, terminal_soc):
    """Require a nonempty complete schedule with explicit cyclic storage targets."""
    check_soc(plant.storage, initial_soc)
    check_soc(plant.storage, terminal_soc)
    if initial_soc != terminal_soc:
        raise ValueError("initial and terminal SOC targets must be identical")

    results = []
    soc = initial_soc
    for hour, dispatch in zip(hours, dispatches, strict=True):
        result = evaluate_hour(plant, hour, dispatch, soc)
        results.append(result)
        soc = result.storage.closing_soc
    if not results:
        raise ValueError("schedule must contain at least one hour")
    if not math.isclose(soc, terminal_soc, rel_tol=0, abs_tol=ABS_TOL):
        raise ValueError("closing SOC does not match the terminal target")
    return tuple(results)
