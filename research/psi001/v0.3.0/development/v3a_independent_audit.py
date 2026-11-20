"""Independent analytical auditor for V3-A5; never imports implementation under audit."""
from decimal import Decimal

PRICES = ("0", "40", "74.99", "75", "80", "100")

def audit_row(price_text):
    p = Decimal(price_text)
    if not p.is_finite() or p < 0:
        raise ValueError("invalid price")
    demand = Decimal("6")
    supply = Decimal("10")
    capacity = Decimal("8")
    efficiency = Decimal("0.8")
    pump = Decimal("5")
    boiler_unit = Decimal("100")
    optimum_flow = min(supply, capacity, demand / efficiency)
    accepted = p + pump < efficiency * boiler_unit
    flow = optimum_flow if accepted else Decimal("0")
    delivered = efficiency * flow
    loss = flow - delivered
    boiler = demand - delivered
    curtailed = supply - flow
    operating_cost = flow * pump + boiler * boiler_unit
    optimal_cost = optimum_flow * pump
    assert flow == delivered + loss
    assert demand == delivered + boiler
    assert supply == flow + curtailed
    assert flow <= capacity
    return {"price":str(p), "accepted":accepted, "flow":str(flow),
            "cost":str(operating_cost), "central_cost":str(optimal_cost),
            "gross_gap":str(operating_cost - optimal_cost), "logical_messages":2}

def audit_all():
    return [audit_row(price) for price in PRICES]

if __name__ == "__main__":
    import json
    print(json.dumps(audit_all(), sort_keys=True, indent=2))
