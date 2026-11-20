"""PSI-001 v0.2.0 annual synthetic dispatch comparison.

Python 3.10+, standard library only. Demand must be nonnegative.
Finite negative market prices and decision tariffs are allowed.
"""
import json
import math

HOURS = 8760
COP = 2.5
BOILER_COST = 45  # synthetic currency units per MWh of useful heat
BOILER_LIMIT = 100  # MWh per hourly interval
PUMP_LIMIT = 18  # MWh of electricity per hourly interval
IMPORT_LIMIT = 95  # MWh per hourly interval
FLAT_TARIFF = 65
OVERHEAD = 100_000
MINIMUM_NET_SAVINGS_SHARE = 0.01
EPSILON = 1e-8

SCENARIOS = ("baseline", "cold_snap", "thermal_trunk_outage")


def normalized(values, annual_total):
    scale = annual_total / math.fsum(values)
    return tuple(value * scale for value in values)


def inputs():
    seasonal = [math.cos(2 * math.pi * (h // 24) / 365) for h in range(HOURS)]
    peak = [17 <= h % 24 < 22 for h in range(HOURS)]
    electric = normalized([60 + 8 * winter + 15 * evening
                           for winter, evening in zip(seasonal, peak)], 500_000)
    temperature = [12 - 11 * winter for winter in seasonal]
    heat = normalized([max(0, 18 - temp) for temp in temperature], 300_000)
    prices = [55 + 15 * winter + 70 * evening
              for winter, evening in zip(seasonal, peak)]
    return electric, heat, prices


def finite_number(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a finite number")
    try:
        finite = math.isfinite(value)
    except OverflowError:
        finite = False
    if not finite:
        raise ValueError(f"{name} must be a finite number")


def validate_hourly_inputs(expected_hours, electric, heat, prices):
    if type(expected_hours) is not int or expected_hours <= 0:
        raise ValueError("expected_hours must be a positive integer")
    for name, series in (("electric", electric), ("heat", heat), ("prices", prices)):
        try:
            length = len(series)
        except TypeError as error:
            raise ValueError(f"{name} must be a sized hourly series") from error
        if length != expected_hours:
            raise ValueError(f"{name} must contain exactly {expected_hours} hours; got {length}")
        for hour, value in enumerate(series):
            label = f"{name}[{hour}]"
            finite_number(value, label)
            if name != "prices" and value < 0:
                raise ValueError(f"{label} must be nonnegative")


def validate_parameters():
    for name, value in (("COP", COP), ("BOILER_LIMIT", BOILER_LIMIT),
                        ("PUMP_LIMIT", PUMP_LIMIT), ("IMPORT_LIMIT", IMPORT_LIMIT),
                        ("BOILER_COST", BOILER_COST), ("OVERHEAD", OVERHEAD),
                        ("EPSILON", EPSILON), ("MINIMUM_NET_SAVINGS_SHARE",
                                                MINIMUM_NET_SAVINGS_SHARE)):
        finite_number(value, name)
        if value < 0:
            raise ValueError(f"{name} must be nonnegative")
    if COP == 0 or EPSILON == 0:
        raise ValueError("COP and EPSILON must be positive")
    if MINIMUM_NET_SAVINGS_SHARE > 1:
        raise ValueError("MINIMUM_NET_SAVINGS_SHARE must be at most 1")


def run(scenario, baseline_tariff, electric, heat, prices, *, expected_hours=HOURS):
    """Run the annual horizon by default, or an explicitly sized test horizon."""
    if scenario not in SCENARIOS:
        raise ValueError(f"unknown scenario: {scenario!r}")
    if not callable(baseline_tariff):
        raise ValueError("baseline_tariff must be callable")
    validate_parameters()
    validate_hourly_inputs(expected_hours, electric, heat, prices)
    totals = {model: {"dispatch_cost": 0.0, "unserved_heat_mwh": 0.0,
                      "unserved_electric_mwh": 0.0, "pump_electric_mwh": 0.0}
              for model in ("independent", "coordinated")}
    heat_total = 0.0
    for hour, (load, useful_heat, price) in enumerate(zip(electric, heat, prices, strict=True)):
        if scenario == "cold_snap" and hour < 72:
            useful_heat *= 1.30
        heat_total += useful_heat
        trunk_online = scenario != "thermal_trunk_outage" or hour >= 48
        electric_served = min(load, IMPORT_LIMIT)
        pump_bound = min(PUMP_LIMIT if trunk_online else 0,
                         IMPORT_LIMIT - electric_served, useful_heat / COP)
        minimum_pump = min(pump_bound, max(0, useful_heat - BOILER_LIMIT) / COP)

        # Service has priority over cost. With no storage or ramping constraints,
        # the hourly cost is linear, so its minimum is at one of these endpoints.
        independent_price = baseline_tariff(hour, price)
        finite_number(independent_price, f"baseline_tariff({hour})")
        for model, decision_price in (("independent", independent_price),
                                      ("coordinated", price)):
            pump = pump_bound if decision_price < BOILER_COST * COP else minimum_pump
            boiler = min(BOILER_LIMIT, max(0, useful_heat - COP * pump))
            imports = electric_served + pump
            unmet_heat = max(0, useful_heat - boiler - COP * pump)
            unmet_electric = max(0, load - electric_served)
            assert imports <= IMPORT_LIMIT + EPSILON
            assert abs(imports - pump + unmet_electric - load) < EPSILON
            assert abs(COP * pump + boiler + unmet_heat - useful_heat) < EPSILON
            row = totals[model]
            row["dispatch_cost"] += imports * price + boiler * BOILER_COST
            row["unserved_heat_mwh"] += unmet_heat
            row["unserved_electric_mwh"] += unmet_electric
            row["pump_electric_mwh"] += pump

    a, b = totals["independent"], totals["coordinated"]
    a["total_cost"] = a["dispatch_cost"]
    b["total_cost"] = b["dispatch_cost"] + OVERHEAD
    savings = a["total_cost"] - b["total_cost"]
    threshold = a["total_cost"] * MINIMUM_NET_SAVINGS_SHARE
    service_met = all(row[key] <= EPSILON for row in totals.values()
                      for key in ("unserved_heat_mwh", "unserved_electric_mwh"))
    return {"heat_demand_mwh": heat_total, **totals, "net_savings": savings,
            "break_even_overhead": a["dispatch_cost"] - b["dispatch_cost"],
            "minimum_net_savings": threshold, "service_met": service_met,
            "favorable": service_met and savings >= threshold}


def main():
    electric, heat, prices = inputs()
    assert math.isclose(math.fsum(electric), 500_000)
    assert math.isclose(math.fsum(heat), 300_000)
    campaigns = {}
    for name, tariff in (("flat_tariff", lambda hour, price: FLAT_TARIFF),
                         ("hourly_tariff", lambda hour, price: price)):
        campaigns[name] = {scenario: run(scenario, tariff, electric, heat, prices)
                           for scenario in SCENARIOS}
    for case in campaigns["hourly_tariff"].values():
        assert abs(case["break_even_overhead"]) < EPSILON
        assert abs(case["net_savings"] + OVERHEAD) < EPSILON
    assert all(case["service_met"] for campaign in campaigns.values()
               for case in campaign.values())
    print(json.dumps({"hours": HOURS, "coordination_overhead": OVERHEAD,
                      "minimum_net_savings_share": MINIMUM_NET_SAVINGS_SHARE,
                      "units": "synthetic currency units and MWh",
                      "campaigns": campaigns}, indent=2))


if __name__ == "__main__":
    main()
