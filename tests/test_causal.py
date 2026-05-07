"""Unit tests for SYNAPSES causal model functions."""

import unittest

from synapses import crime_from_price_and_inequality, price_from_food_supply


class CausalModelTests(unittest.TestCase):
    """Verify price and crime causal functions are deterministic."""

    def test_low_food_supply_increases_price(self) -> None:
        self.assertEqual(price_from_food_supply(49, base_price=10), 11)

    def test_moderate_food_supply_keeps_price(self) -> None:
        self.assertEqual(price_from_food_supply(80, base_price=10), 10)

    def test_high_food_supply_decreases_price(self) -> None:
        self.assertEqual(price_from_food_supply(121, base_price=10), 9)

    def test_price_has_minimum_bound(self) -> None:
        self.assertEqual(price_from_food_supply(121, base_price=1), 1)

    def test_crime_increases_with_high_price_and_inequality(self) -> None:
        self.assertEqual(crime_from_price_and_inequality(price=15, inequality=30), 35)

    def test_crime_decreases_with_low_price_pressure(self) -> None:
        self.assertEqual(crime_from_price_and_inequality(price=7, inequality=30), 27)

    def test_crime_is_clamped_to_bounds(self) -> None:
        self.assertEqual(crime_from_price_and_inequality(price=200, inequality=50), 100)
        self.assertEqual(crime_from_price_and_inequality(price=0, inequality=5), 0)


if __name__ == "__main__":
    unittest.main()
