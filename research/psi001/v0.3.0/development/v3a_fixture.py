"""Deterministic, one-hour PSI-001 V3-A analytical fixtures.

Synthetic units only. Internal bilateral payments are transfers, not system costs.
"""
from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class Fixture:
    surplus_mwh: float = 10.0
    demand_mwh: float = 6.0
    link_capacity_mwh: float = 8.0
    delivery_efficiency: float = 0.8
    pumping_cost_per_input_mwh: float = 5.0
    boiler_cost_per_delivered_mwh: float = 100.0

    def __post_init__(self):
        values = vars(self)
        if any(not isfinite(v) for v in values.values()):
            raise ValueError("All inputs must be finite")
        if any(v < 0 for k, v in values.items() if k != "delivery_efficiency"):
            raise ValueError("Negative physical or cost parameter")
        if not (0 < self.delivery_efficiency <= 1):
            raise ValueError("Efficiency must be in (0, 1]")

    @property
    def max_flow(self):
        return min(self.surplus_mwh, self.link_capacity_mwh,
                   self.demand_mwh / self.delivery_efficiency)


def evaluate(flow_mwh: float, f: Fixture = Fixture()) -> dict:
    if not isfinite(flow_mwh) or flow_mwh < 0 or flow_mwh > f.max_flow + 1e-10:
        raise ValueError("Infeasible link flow")
    delivered = flow_mwh * f.delivery_efficiency
    lost = flow_mwh - delivered
    boiler = max(0.0, f.demand_mwh - delivered)
    cost = flow_mwh * f.pumping_cost_per_input_mwh + boiler * f.boiler_cost_per_delivered_mwh
    return {"flow": flow_mwh, "delivered": delivered, "lost": lost,
            "boiler": boiler, "curtailed": f.surplus_mwh - flow_mwh,
            "cost": cost}


def no_exchange(f: Fixture = Fixture()) -> dict:
    return evaluate(0.0, f)


def central_dispatch(f: Fixture = Fixture()) -> dict:
    marginal_saving = f.boiler_cost_per_delivered_mwh * f.delivery_efficiency
    return evaluate(f.max_flow if marginal_saving > f.pumping_cost_per_input_mwh else 0.0, f)


def bilateral_exchange(price_per_input_mwh: float = 40.0,
                       f: Fixture = Fixture()) -> dict:
    """Seller offers curtailed heat for any nonnegative price; buyer accepts if
    avoided boiler cost exceeds price plus pumping. Tie breaks to no exchange.
    """
    if not isfinite(price_per_input_mwh) or price_per_input_mwh < 0:
        raise ValueError("Invalid transfer price")
    buyer_value = f.boiler_cost_per_delivered_mwh * f.delivery_efficiency
    flow = f.max_flow if buyer_value > price_per_input_mwh + f.pumping_cost_per_input_mwh else 0.0
    result = evaluate(flow, f)
    result["internal_transfer"] = flow * price_per_input_mwh
    return result


def comparison(f: Fixture = Fixture(), price: float = 40.0) -> dict:
    baseline = no_exchange(f)
    central = central_dispatch(f)
    bilateral = bilateral_exchange(price, f)
    return {"network_exchange_value": baseline["cost"] - central["cost"],
            "coordination_mechanism_value": bilateral["cost"] - central["cost"],
            "baseline": baseline, "central": central, "bilateral": bilateral}
