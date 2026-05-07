"""Metrics for SYNAPSES agents and simulation histories.

The functions in this module are stateless, deterministic, and dependency-free
so they can be tested independently from the simulation engine.
"""

from __future__ import annotations

from typing import Any, Iterable, Mapping, Sequence

from .agent import Agent


def gini_coefficient(values: Iterable[int | float]) -> float:
    """Calculate the Gini coefficient for a collection of non-negative values.

    Args:
        values: Numeric values, usually agent wealth values.

    Returns:
        A float between 0.0 and 1.0 where 0.0 means perfect equality.
    """
    sorted_values = sorted(float(value) for value in values)
    if not sorted_values:
        return 0.0

    if sorted_values[0] < 0:
        raise ValueError("Gini coefficient requires non-negative values.")

    total = sum(sorted_values)
    if total == 0:
        return 0.0

    weighted_sum = sum(
        index * value for index, value in enumerate(sorted_values, start=1)
    )
    count = len(sorted_values)
    return (2 * weighted_sum) / (count * total) - (count + 1) / count


def average_satisfaction(agents: Iterable[Agent]) -> float:
    """Calculate average satisfaction across agents.

    Args:
        agents: Agents with a ``satisfaction`` attribute.

    Returns:
        Mean satisfaction, or 0.0 when no agents are provided.
    """
    satisfaction_values = [agent.satisfaction for agent in agents]
    if not satisfaction_values:
        return 0.0

    return sum(satisfaction_values) / len(satisfaction_values)


def track_crime(history: Sequence[Mapping[str, Any]]) -> list[int]:
    """Extract crime-rate values from simulation state history.

    Args:
        history: Sequence of simulation history entries containing an
            ``environment`` mapping with a ``crime_rate`` value.

    Returns:
        Crime-rate values in step order. Missing or non-numeric values become 0.
    """
    return [_crime_rate_from_entry(entry) for entry in history]


def _crime_rate_from_entry(entry: Mapping[str, Any]) -> int:
    """Read one integer crime-rate value from a history entry."""
    environment = entry.get("environment", {})
    if not isinstance(environment, Mapping):
        return 0

    crime_rate = environment.get("crime_rate", 0)
    if isinstance(crime_rate, bool):
        return int(crime_rate)

    if isinstance(crime_rate, (int, float)):
        return int(crime_rate)

    return 0
