"""Bridge from integrated simulation metrics to RL director observations."""

from __future__ import annotations

from .rl import DirectorObservation


def metrics_to_observation(metrics: dict | None) -> DirectorObservation:
    """Project integrated-simulation metrics into RL observation space [0, 1]."""
    data = metrics or {}
    gini = _clamp01(float(data.get("gini", 0.0)))
    crime_rate = _clamp01(float(data.get("crime_rate", 0.0)) / 100.0)
    avg_sat = _clamp01(float(data.get("average_satisfaction", 0.0)) / 100.0)
    food_supply = max(0.0, float(data.get("food_supply", 0.0)))
    price = max(1.0, float(data.get("price", 1.0)))

    unemployment = _clamp01((price - 1.0) / 99.0)
    resource_distribution = _clamp01(food_supply / (food_supply + price + 1.0))
    neighborhood_disparity = _clamp01((gini + crime_rate) / 2.0)
    regional_stability = _clamp01((1.0 - crime_rate) * 0.6 + avg_sat * 0.4)

    return DirectorObservation(
        inequality=gini,
        crime=crime_rate,
        regional_stability=regional_stability,
        resource_distribution=resource_distribution,
        unemployment=unemployment,
        social_satisfaction=avg_sat,
        neighborhood_disparity=neighborhood_disparity,
    )


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))
