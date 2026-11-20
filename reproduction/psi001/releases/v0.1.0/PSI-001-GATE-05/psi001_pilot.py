"""Two-hour synthetic PSI-001 dispatch check. Run with Python 3.10+."""
import json
from itertools import product

ELECTRIC_LOAD = (2, 2)  # MWh per one-hour interval
HEAT_LOAD = (2, 2)  # MWh of useful heat
HEAT_PUMP_COP = 2
BOILER_COST = 4  # synthetic cost units per MWh of useful heat
COORDINATION_COST = 1
MINIMUM_SAVINGS = 1


def dispatch(prices, import_limits, coordinated):
    # Independent heating minimizes its own bill at a flat tariff of 5 per
    # MWh. Electricity accepts requests up to its spare import capacity.
    # The boiler supplies any residual demand at each hour.
    spare = tuple(limit - load for limit, load in zip(import_limits, ELECTRIC_LOAD))
    assert all(capacity >= 0 for capacity in spare)
    boiler_only = (0,) * len(HEAT_LOAD)
    options = product(*(range(min(heat // HEAT_PUMP_COP, capacity) + 1)
                        for heat, capacity in zip(HEAT_LOAD, spare)))
    if not coordinated:
        flat_heat_pump_tariff = 5
        requests = (tuple(heat // HEAT_PUMP_COP for heat in HEAT_LOAD)
                    if flat_heat_pump_tariff < BOILER_COST * HEAT_PUMP_COP
                    else boiler_only)
        options = [tuple(min(request, capacity)
                         for request, capacity in zip(requests, spare))]

    def schedule(pump_power):
        imports = tuple(load + pump for load, pump in zip(ELECTRIC_LOAD, pump_power))
        boiler_heat = tuple(heat - HEAT_PUMP_COP * pump
                            for heat, pump in zip(HEAT_LOAD, pump_power))
        assert all(0 <= power <= limit for power, limit in zip(imports, import_limits))
        assert all(boiler >= 0 for boiler in boiler_heat)
        for hour, (power, pump, boiler) in enumerate(zip(imports, pump_power, boiler_heat)):
            assert power - pump == ELECTRIC_LOAD[hour]
            assert pump * HEAT_PUMP_COP + boiler == HEAT_LOAD[hour]
        cost = sum(power * price for power, price in zip(imports, prices))
        cost += sum(boiler_heat) * BOILER_COST
        return {"imports_mwh": imports, "pump_power_mwh": pump_power,
                "boiler_heat_mwh": boiler_heat, "unserved_mwh": 0,
                "dispatch_cost": cost}

    result = min(map(schedule, options), key=lambda row: row["dispatch_cost"])
    result["total_cost"] = result["dispatch_cost"] + (COORDINATION_COST if coordinated else 0)
    return result


def compare(prices, limits):
    independent = dispatch(prices, limits, False)
    coordinated = dispatch(prices, limits, True)
    net_savings = independent["total_cost"] - coordinated["total_cost"]
    return {"prices_per_mwh": prices, "import_limits_mwh": limits,
            "independent": independent, "coordinated": coordinated,
            "break_even_coordination_cost":
                independent["dispatch_cost"] - coordinated["dispatch_cost"],
            "net_savings": net_savings,
            "meets_savings_threshold": net_savings >= MINIMUM_SAVINGS}


if __name__ == "__main__":
    cases = {
        "price_variation": compare((2, 10), (3, 3)),
        "no_dispatch_flexibility": compare((2, 10), (2, 2)),
        "low_price_hour_import_restriction": compare((2, 10), (2, 3)),
    }
    assert [cases[name]["net_savings"] for name in cases] == [1, -1, 1]
    assert cases["price_variation"]["independent"]["total_cost"] == 36
    assert cases["price_variation"]["coordinated"]["total_cost"] == 35
    assert cases["no_dispatch_flexibility"]["independent"]["dispatch_cost"] == 40
    assert cases["no_dispatch_flexibility"]["coordinated"]["dispatch_cost"] == 40
    print(json.dumps({"coordination_cost": COORDINATION_COST,
                      "minimum_savings": MINIMUM_SAVINGS, "cases": cases}, indent=2))
