"""PSI-001 V3-A5 bounded bilateral protocol; deterministic synthetic fixture."""
from dataclasses import dataclass
from math import isfinite
from v3a_fixture import Fixture, evaluate, central_dispatch


@dataclass(frozen=True)
class Message:
    sender: str
    recipient: str
    kind: str
    value: float


def bilateral_one_round(price: float, fixture: Fixture = Fixture()) -> dict:
    """One posted-price proposal and one buyer response; both know fixture data."""
    if not isfinite(price) or price < 0:
        raise ValueError("Price must be finite and nonnegative")
    offer = Message("A", "B", "offer_price_per_input_mwh", price)
    buyer_value = fixture.boiler_cost_per_delivered_mwh * fixture.delivery_efficiency
    accepted = buyer_value > price + fixture.pumping_cost_per_input_mwh
    reply = Message("B", "A", "accept" if accepted else "reject", 1.0 if accepted else 0.0)
    result = evaluate(fixture.max_flow if accepted else 0.0, fixture)
    return {"dispatch": result, "messages": (offer, reply),
            "message_count": 2, "internal_payment": result["flow"] * price}


def compare_price(price: float, fixture: Fixture = Fixture()) -> dict:
    bilateral = bilateral_one_round(price, fixture)
    central = central_dispatch(fixture)
    gross_gap = bilateral["dispatch"]["cost"] - central["cost"]
    return {"price": price, "bilateral": bilateral, "central": central,
            "gross_protocol_gap": gross_gap,
            "break_even_incremental_overhead": gross_gap}


def sweep(prices=(0, 40, 74.99, 75, 80, 100), fixture: Fixture = Fixture()):
    return [compare_price(p, fixture) for p in prices]
