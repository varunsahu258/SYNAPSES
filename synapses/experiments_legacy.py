"""Experiment orchestration for comparing simulation director strategies.

The module is independent from FastAPI so experiment behavior can be tested
without web dependencies. Each experiment starts from the same deterministic
agents and environment, then compares metrics across director strategies.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any, Mapping

from .agent import Agent
from .director import DirectorAI, Intervention
from .environment import Environment
from .integration import run_full_simulation

ExperimentResult = dict[str, Any]
ComparisonResult = dict[str, Any]


@dataclass(frozen=True)
class NoDirector:
    """Director strategy that intentionally makes no interventions."""

    def recommend(self, global_metrics: Mapping[str, Any] | None) -> list[Intervention]:
        """Return an empty intervention list for any metric state."""
        return []


@dataclass
class RandomDirector:
    """Deterministic pseudo-random intervention strategy.

    A local random generator keeps this strategy reproducible and isolated from
    module-level random state.
    """

    seed: int = 42

    def __post_init__(self) -> None:
        """Initialize local pseudo-random state after dataclass construction."""
        self._random = random.Random(self.seed)

    def recommend(self, global_metrics: Mapping[str, Any] | None) -> list[Intervention]:
        """Return one pseudo-random intervention action."""
        options: tuple[Intervention, ...] = (
            {"action": "monitor", "reason": "random_choice"},
            {"action": "redistribute_resources", "reason": "random_choice"},
            {"action": "fund_public_services", "reason": "random_choice"},
            {"action": "increase_safety_programs", "reason": "random_choice"},
        )
        return [dict(self._random.choice(options))]


def run_experiment(
    num_agents: int,
    steps: int,
    tax_rate: float = 0.0,
) -> ComparisonResult:
    """Run no-director, random, and director-based simulation variants.

    Args:
        num_agents: Number of deterministic agents per variant. Must be >= 1.
        steps: Number of steps per variant. Must be >= 0.
        tax_rate: Optional initial wealth redistribution rate in the range 0..1.

    Returns:
        Comparison dictionary containing per-variant metrics over time and final
        metric summaries.
    """
    _validate_experiment_input(num_agents, steps, tax_rate)
    experiments = {
        "no_director": _run_variant(num_agents, steps, tax_rate, NoDirector()),
        "random": _run_variant(num_agents, steps, tax_rate, RandomDirector()),
        "director_based": _run_variant(num_agents, steps, tax_rate, DirectorAI()),
    }
    return {
        "experiments": experiments,
        "comparison": _comparison_summary(experiments),
    }


def build_agents(num_agents: int, tax_rate: float = 0.0) -> list[Agent]:
    """Create deterministic agents and apply optional initial wealth tax."""
    _validate_experiment_input(num_agents, steps=0, tax_rate=tax_rate)
    base_wealth = _initial_wealth_values(num_agents)
    taxed_wealth = _apply_wealth_tax(base_wealth, tax_rate)
    return [
        Agent(
            wealth=wealth,
            health=80,
            satisfaction=_initial_satisfaction(index),
        )
        for index, wealth in enumerate(taxed_wealth)
    ]


def _run_variant(
    num_agents: int,
    steps: int,
    tax_rate: float,
    director: Any,
) -> ExperimentResult:
    """Run one experiment variant from fresh deterministic starting state."""
    metrics_over_time = run_full_simulation(
        steps=steps,
        agents=build_agents(num_agents, tax_rate),
        environment=Environment(food_supply=100, price=10, crime_rate=10),
        director=director,
    )
    return {
        "metrics_over_time": metrics_over_time,
        "final_metrics": _final_metrics(metrics_over_time),
    }


def _final_metrics(metrics_over_time: list[dict[str, Any]]) -> dict[str, Any]:
    """Return final comparable metrics from a metrics series."""
    if not metrics_over_time:
        return {
            "step": 0,
            "gini": 0.0,
            "average_satisfaction": 0.0,
            "crime_rate": 0,
            "interventions": [],
        }

    final = metrics_over_time[-1]
    return {
        "step": final["step"],
        "gini": final["gini"],
        "average_satisfaction": final["average_satisfaction"],
        "crime_rate": final["crime_rate"],
        "interventions": final["interventions"],
    }


def _comparison_summary(experiments: Mapping[str, ExperimentResult]) -> dict[str, Any]:
    """Build compact final-metric comparison across variants."""
    return {
        name: result["final_metrics"]
        for name, result in experiments.items()
    }


def _validate_experiment_input(num_agents: int, steps: int, tax_rate: float) -> None:
    """Validate experiment input for non-API callers."""
    if num_agents < 1:
        raise ValueError("num_agents must be at least 1.")

    if steps < 0:
        raise ValueError("steps must be zero or greater.")

    if tax_rate < 0 or tax_rate > 1:
        raise ValueError("tax_rate must be between 0 and 1.")


def _initial_wealth_values(num_agents: int) -> list[int]:
    """Return deterministic initial wealth values for generated agents."""
    if num_agents == 1:
        return [50]

    return [20 + index * 10 for index in range(num_agents)]


def _apply_wealth_tax(wealth_values: list[int], tax_rate: float) -> list[int]:
    """Redistribute initial wealth toward the mean by ``tax_rate``."""
    mean_wealth = sum(wealth_values) / len(wealth_values)
    return [
        round(wealth * (1 - tax_rate) + mean_wealth * tax_rate)
        for wealth in wealth_values
    ]


def _initial_satisfaction(index: int) -> int:
    """Return deterministic satisfaction values with mild variation."""
    return 45 + (index % 3) * 10
