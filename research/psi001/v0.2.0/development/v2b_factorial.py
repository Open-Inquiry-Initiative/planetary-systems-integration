"""Preregistered PSI-001 V2-B pricing-information and overhead controls."""
import json
import math

import psi001_annual as model


def cost_contrasts(cells, metric):
    """Savings relative to the limited-information independent cell."""
    a_l = cells["limited"]["independent"][metric]
    b_l = cells["limited"]["coordinated_control"][metric]
    a_h = cells["shared_hourly"]["independent"][metric]
    b_h = cells["shared_hourly"]["coordinated_control"][metric]
    information = a_l - a_h
    coordination = a_l - b_l
    interaction = (b_l - b_h) - (a_l - a_h)
    combined = a_l - b_h
    if not math.isclose(combined, math.fsum((information, coordination, interaction)),
                        rel_tol=0, abs_tol=1e-8):
        raise ArithmeticError(f"{metric} contrasts do not reconcile")
    return {
        "information_only": information,
        "coordination_only": coordination,
        "interaction": interaction,
        "combined": combined,
    }


def compare(scenario, electric, heat, prices, *, expected_hours=model.HOURS):
    """Score four cells at realized prices, with dispatch shared within each row."""
    cells = {}
    for information, decision_price in (
        ("limited", lambda hour, price: model.FLAT_TARIFF),
        ("shared_hourly", lambda hour, price: price),
    ):
        # V2-A's independent path permits arbitrary decision prices and always
        # scores dispatch at realized prices. Both V2-B planners use that rule.
        dispatch = model.run(scenario, decision_price, electric, heat, prices,
                             expected_hours=expected_hours)["independent"]
        cells[information] = {
            "independent": {**dispatch, "overhead": 0},
            "coordinated_control": {
                **dispatch,
                "overhead": model.OVERHEAD,
                "total_cost": dispatch["dispatch_cost"] + model.OVERHEAD,
            },
        }
    return {
        "cells": cells,
        "savings_without_overhead": cost_contrasts(cells, "dispatch_cost"),
        "savings_with_overhead": cost_contrasts(cells, "total_cost"),
    }


def main():
    electric, heat, prices = model.inputs()
    print(json.dumps({
        "hours": model.HOURS,
        "coordination_mechanism": "none",
        "coordination_overhead": model.OVERHEAD,
        "units": "synthetic currency units and MWh",
        "scenarios": {
            scenario: compare(scenario, electric, heat, prices)
            for scenario in model.SCENARIOS
        },
    }, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
