"""Run: python -m unittest discover -s research/psi001/v0.3.0/development -p 'test_v3a*.py'"""
import unittest
from dataclasses import replace
from v3a_fixture import Fixture, evaluate, no_exchange, central_dispatch, bilateral_exchange, comparison


class TestV3A(unittest.TestCase):
    def test_fixture(self):
        c = comparison()
        self.assertAlmostEqual(c["baseline"]["cost"], 600)
        self.assertAlmostEqual(c["central"]["cost"], 37.5)
        self.assertAlmostEqual(c["bilateral"]["cost"], 37.5)
        self.assertAlmostEqual(c["network_exchange_value"], 562.5)
        self.assertAlmostEqual(c["coordination_mechanism_value"], 0)

    def test_conservation(self):
        f = Fixture()
        for policy in (central_dispatch, bilateral_exchange, no_exchange):
            result = policy(f=f)
            self.assertAlmostEqual(result["flow"], result["delivered"] + result["lost"])
            self.assertAlmostEqual(f.demand_mwh, result["delivered"] + result["boiler"])
            self.assertAlmostEqual(f.surplus_mwh, result["flow"] + result["curtailed"])
            self.assertLessEqual(result["flow"], f.link_capacity_mwh)

    def test_no_link(self):
        f = replace(Fixture(), link_capacity_mwh=0)
        self.assertAlmostEqual(comparison(f)["network_exchange_value"], 0)
        self.assertAlmostEqual(comparison(f)["coordination_mechanism_value"], 0)

    def test_no_surplus(self):
        f = replace(Fixture(), surplus_mwh=0)
        self.assertAlmostEqual(comparison(f)["network_exchange_value"], 0)

    def test_high_pumping_cost(self):
        f = replace(Fixture(), pumping_cost_per_input_mwh=100)
        self.assertAlmostEqual(central_dispatch(f)["flow"], 0)
        self.assertAlmostEqual(bilateral_exchange(f=f)["flow"], 0)

    def test_expensive_bilateral_price(self):
        self.assertAlmostEqual(bilateral_exchange(price_per_input_mwh=100)["flow"], 0)

    def test_reject_infeasible(self):
        for x in (-1, 8, float("nan"), float("inf")):
            with self.assertRaises(ValueError):
                evaluate(x)

    def test_reject_invalid_fixture(self):
        for changes in ({"delivery_efficiency": 0}, {"delivery_efficiency": 1.1},
                        {"surplus_mwh": -1}, {"demand_mwh": float("nan")}):
            with self.assertRaises(ValueError):
                replace(Fixture(), **changes)

    def test_internal_payment_not_system_cost(self):
        r = bilateral_exchange()
        self.assertAlmostEqual(r["internal_transfer"], 300)
        self.assertAlmostEqual(r["cost"], 37.5)


if __name__ == "__main__":
    unittest.main()
