"""Deterministic environment model for SYNAPSES simulations.

The :class:`Environment` class tracks only food supply, price, and crime rate.
Its update rules are deliberately small and explicit so callers can test the
module independently from agents or workflow helpers.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from .causal import price_from_food_supply


@dataclass
class Environment:
    """A simple environment with food, price, and public-safety signals.

    Attributes:
        food_supply: Available food units in the environment.
        price: Current unit price for food or basic goods.
        crime_rate: Public-safety risk score clamped between 0 and 100.
    """

    food_supply: int = 100
    price: int = 10
    crime_rate: int = 10

    def update(self, actions: Iterable[Mapping[str, Any]] | Mapping[str, Any] | None) -> dict[str, int]:
        """Apply action effects and return the updated environment state.

        Args:
            actions: A single action dictionary, an iterable of action
                dictionaries, or ``None``. Recognized action names are ``work``,
                ``rest``, ``socialize``, and ``maintain``.

        Returns:
            Dictionary containing ``food_supply``, ``price``, and
            ``crime_rate`` after deterministic updates.
        """
        action_names = _action_names(actions)

        for action in action_names:
            self._apply_action(action)

        self._rebalance_price()
        self._clamp_values()
        return self.state()

    def state(self) -> dict[str, int]:
        """Return a serializable snapshot of the environment."""
        return {
            "food_supply": self.food_supply,
            "price": self.price,
            "crime_rate": self.crime_rate,
        }

    def _apply_action(self, action: str) -> None:
        """Apply one recognized action to environment variables."""
        if action == "work":
            self.food_supply += 5
            self.crime_rate -= 1
            return

        if action == "rest":
            self.food_supply -= 1
            self.crime_rate -= 2
            return

        if action == "socialize":
            self.food_supply -= 2
            self.crime_rate -= 1
            return

        if action == "maintain":
            self.food_supply -= 1

    def _rebalance_price(self) -> None:
        """Adjust price using the food-supply causal model."""
        self.price = price_from_food_supply(self.food_supply, self.price)

    def _clamp_values(self) -> None:
        """Keep environment values within practical deterministic bounds."""
        self.food_supply = max(0, self.food_supply)
        self.price = max(1, self.price)
        self.crime_rate = min(100, max(0, self.crime_rate))


def _action_names(actions: Iterable[Mapping[str, Any]] | Mapping[str, Any] | None) -> tuple[str, ...]:
    """Extract action names from supported action inputs.

    Unknown or malformed action entries become empty strings and therefore have
    no effect during updates.
    """
    if actions is None:
        return ()

    if isinstance(actions, Mapping):
        return (_as_action_name(actions),)

    return tuple(_as_action_name(action) for action in actions)


def _as_action_name(action: Mapping[str, Any]) -> str:
    """Read a string action name from an action dictionary."""
    name = action.get("action", "")
    return name if isinstance(name, str) else ""
