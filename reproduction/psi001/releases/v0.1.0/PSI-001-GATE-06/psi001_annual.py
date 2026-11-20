"""PSI-001 annual synthetic dispatch comparison. Python 3.10+, no dependencies."""
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


def run(scenario, baseline_tariff, electric, heat, prices):
    totals = {model: {"dispatch_cost": 0.0, "unserved_heat_mwh": 0.0,
                      "unserved_electric_mwh": 0.0, "pump_electric_mwh": 0.0}
              for model in ("independent", "coordinated")}
    heat_total = 0.0
    for hour, (load, useful_heat, price) in enumerate(zip(electric, heat, prices)):
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
        for model, decision_price in (("independent", baseline_tariff(hour, price)),
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
