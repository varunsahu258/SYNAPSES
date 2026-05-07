"""Causal model functions for SYNAPSES simulations.

The functions in this module are intentionally stateless and deterministic.
They can be tested independently and reused by environment or simulation code
without creating circular dependencies.
"""

from __future__ import annotations


def price_from_food_supply(food_supply: int, base_price: int = 10) -> int:
    """Calculate price as a simple causal function of food supply.

    Low food supply increases price, high food supply decreases price, and
    moderate food supply keeps the base price unchanged.

    Args:
        food_supply: Available food units.
        base_price: Neutral price when supply is moderate.

    Returns:
        Price clamped to a minimum of 1.
    """
    if food_supply < 50:
        return max(1, base_price + 1)

    if food_supply > 120:
        return max(1, base_price - 1)

    return max(1, base_price)


def crime_from_price_and_inequality(price: int, inequality: int) -> int:
    """Calculate crime rate from price pressure and inequality.

    The model is deliberately small: inequality contributes directly, while
    prices above the neutral value of 10 add pressure and prices below 10 reduce
    pressure. The result is clamped to the inclusive range 0..100.

    Args:
        price: Current price level.
        inequality: Inequality score or pressure signal.

    Returns:
        Deterministic crime-rate score between 0 and 100.
    """
    pressure = inequality + (price - 10)
    return min(100, max(0, pressure))
