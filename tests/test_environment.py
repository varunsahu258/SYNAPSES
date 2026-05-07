"""Unit tests for the deterministic Environment module."""

import unittest

from synapses import Environment


class EnvironmentTests(unittest.TestCase):
    """Verify environment updates are deterministic and bounded."""

    def test_work_increases_food_and_reduces_crime(self) -> None:
        environment = Environment(food_supply=100, price=10, crime_rate=10)

        self.assertEqual(
            environment.update({"action": "work"}),
            {"food_supply": 105, "price": 10, "crime_rate": 9},
        )

    def test_multiple_actions_are_applied_in_order(self) -> None:
        environment = Environment(food_supply=100, price=10, crime_rate=10)

        self.assertEqual(
            environment.update([
                {"action": "work"},
                {"action": "rest"},
                {"action": "socialize"},
            ]),
            {"food_supply": 102, "price": 10, "crime_rate": 6},
        )

    def test_low_food_supply_increases_price(self) -> None:
        environment = Environment(food_supply=49, price=10, crime_rate=10)

        self.assertEqual(
            environment.update(None),
            {"food_supply": 49, "price": 11, "crime_rate": 10},
        )

    def test_high_food_supply_decreases_price(self) -> None:
        environment = Environment(food_supply=121, price=10, crime_rate=10)

        self.assertEqual(
            environment.update(None),
            {"food_supply": 121, "price": 9, "crime_rate": 10},
        )

    def test_values_are_clamped_to_bounds(self) -> None:
        environment = Environment(food_supply=0, price=1, crime_rate=1)

        self.assertEqual(
            environment.update([{"action": "rest"}, {"action": "socialize"}]),
            {"food_supply": 0, "price": 2, "crime_rate": 0},
        )

    def test_unknown_actions_have_no_direct_effect(self) -> None:
        environment = Environment(food_supply=100, price=10, crime_rate=10)

        self.assertEqual(
            environment.update({"action": "unknown"}),
            {"food_supply": 100, "price": 10, "crime_rate": 10},
        )


if __name__ == "__main__":
    unittest.main()
