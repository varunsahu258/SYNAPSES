"""Rule-based Director AI for SYNAPSES simulations.

The director consumes global metrics and returns intervention action
dictionaries. Rules are deliberately simple, deterministic, and independent of
the simulation engine so this module can be tested on its own.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

Intervention = dict[str, str]


@dataclass(frozen=True)
class DirectorAI:
    """Choose interventions from global simulation metrics.

    Attributes:
        gini_threshold: Inequality level that triggers redistribution.
        satisfaction_threshold: Average satisfaction level that triggers welfare.
        crime_threshold: Crime level that triggers public-safety support.
    """

    gini_threshold: float = 0.4
    satisfaction_threshold: float = 40.0
    crime_threshold: float = 50.0

    def recommend(self, global_metrics: Mapping[str, Any] | None) -> list[Intervention]:
        """Return intervention actions for the provided global metrics.

        Args:
            global_metrics: Mapping with optional ``gini``,
                ``average_satisfaction``, and ``crime_rate`` values.

        Returns:
            Ordered intervention action dictionaries. If no rule fires, a single
            ``monitor`` action is returned.
        """
        metrics = global_metrics or {}
        interventions: list[Intervention] = []

        if _as_float(metrics.get("gini", 0.0)) > self.gini_threshold:
            interventions.append(
                {"action": "redistribute_resources", "reason": "high_inequality"}
            )

        if _as_float(metrics.get("average_satisfaction", 100.0)) < self.satisfaction_threshold:
            interventions.append(
                {"action": "fund_public_services", "reason": "low_satisfaction"}
            )

        if _as_float(metrics.get("crime_rate", 0.0)) > self.crime_threshold:
            interventions.append(
                {"action": "increase_safety_programs", "reason": "high_crime"}
            )

        if interventions:
            return interventions

        return [{"action": "monitor", "reason": "stable_metrics"}]


def _as_float(value: Any) -> float:
    """Convert numeric metric values to floats; treat other values as zero."""
    if isinstance(value, bool):
        return float(value)

    if isinstance(value, (int, float)):
        return float(value)

    return 0.0
