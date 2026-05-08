"""Integrated simulation runner for SYNAPSES.

This module wires together agents, the environment, causal model functions,
metrics, and the Director AI. It returns metrics over time so callers can inspect
how each deterministic simulation step evolves.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from math import ceil, sqrt
from typing import Any, Iterable, Iterator

from .agent import Agent
from .causal import crime_from_price_and_inequality
from .director import DirectorAI, Intervention
from .environment import Environment
from .metrics import average_satisfaction, gini_coefficient
from .core.spatial import GridWorld

Action = dict[str, str]
MetricsEntry = dict[str, Any]
HistoryEntry = dict[str, Any]


@dataclass
class IntegratedSimulation:
    """Run a full deterministic simulation across all core modules.

    Attributes:
        agents: Agents managed by the simulation.
        environment: Environment that receives agent actions.
        director: Rule-based director that recommends interventions from metrics.
    """

    agents: list[Agent] = field(default_factory=list)
    environment: Environment = field(default_factory=Environment)
    director: DirectorAI = field(default_factory=DirectorAI)
    grid_world: GridWorld = field(default_factory=lambda: GridWorld(width=1, height=1))

    def __init__(
        self,
        agents: Iterable[Agent] | None = None,
        environment: Environment | None = None,
        director: DirectorAI | None = None,
        grid_world: GridWorld | None = None,
    ) -> None:
        """Create an integrated simulation from explicit components."""
        self.agents = list(agents or [])
        self.environment = environment or Environment()
        self.director = director or DirectorAI()
        self.grid_world = grid_world or self._build_grid_world(len(self.agents))
        self._history: list[HistoryEntry] = []
        self._crime_history: list[int] = []
        self._register_agents_in_grid()

    @property
    def history(self) -> tuple[HistoryEntry, ...]:
        """Return immutable access to raw state history entries."""
        return tuple(self._history)

    def run(self, steps: int) -> list[MetricsEntry]:
        """Run the full simulation and return metrics over time.

        Args:
            steps: Number of deterministic steps to execute. Must be non-negative.

        Returns:
            A list of per-step metric entries, including director interventions.
        """
        return list(self.iter_steps(steps))

    def iter_steps(self, steps: int) -> Iterator[MetricsEntry]:
        """Yield one metrics entry after each deterministic simulation step.

        Args:
            steps: Number of deterministic steps to execute. Must be non-negative.

        Yields:
            Per-step metric entries as soon as each step is complete.
        """
        if steps < 0:
            raise ValueError("Simulation steps must be zero or greater.")

        for step_number in range(1, steps + 1):
            yield self._run_step(step_number)

    def _run_step(self, step_number: int) -> MetricsEntry:
        """Run one integrated step and return the metrics entry."""
        actions = self._collect_agent_actions()
        self.environment.update(actions)
        self._apply_causal_crime_rate()

        metrics = self._metrics_entry(step_number)
        interventions = self.director.recommend(metrics)
        self._apply_interventions(interventions)
        self._move_agents()

        history_entry = self._history_entry(step_number, actions)
        self._history.append(history_entry)
        self._crime_history.append(self.environment.crime_rate)

        metrics = self._metrics_entry(step_number)
        metrics["interventions"] = interventions
        metrics["agent_actions"] = actions
        return metrics


    def _apply_interventions(self, interventions: Iterable[Intervention]) -> None:
        """Apply director interventions to the environment deterministically."""
        for intervention in interventions:
            action = intervention.get("action", "")

            if action == "redistribute_resources":
                self.environment.food_supply += 4
                self.environment.price = max(1, self.environment.price - 1)
                continue

            if action == "fund_public_services":
                self.environment.food_supply += 2
                self.environment.crime_rate -= 3
                continue

            if action == "increase_safety_programs":
                self.environment.crime_rate -= 5

        self.environment._clamp_values()

    def _collect_agent_actions(self) -> list[Action]:
        """Call every agent with the current environment-derived state."""
        environment_state = self._agent_environment_state()
        return [agent.act(dict(environment_state)) for agent in self.agents]

    def _register_agents_in_grid(self) -> None:
        """Register all agents deterministically in the spatial grid."""
        for index, agent in enumerate(self.agents):
            default_cell = (index % self.grid_world.width, index // self.grid_world.width)
            current_position = getattr(agent, "position", default_cell)
            position = current_position if self.grid_world.is_valid_cell(current_position) else default_cell
            if not self.grid_world.is_valid_cell(position):
                position = (0, 0)
            agent.position = position
            self.grid_world.register_agent(str(index), position)

    def _move_agents(self) -> None:
        """Move each agent once using local cell utility from neighborhood state."""
        self._sync_cell_signals()
        for index, agent in enumerate(self.agents):
            agent_id = str(index)
            current = self.grid_world.get_agent_cell(agent_id)
            if current is None:
                continue
            candidates = [current, *self.grid_world.neighbors(current, radius=1)]
            next_cell = min(
                candidates,
                key=lambda cell: (-self._cell_utility(cell), cell[1], cell[0]),
            )
            self.grid_world.move_agent(agent_id, next_cell)
            agent.position = next_cell

    def _cell_utility(self, coord: tuple[int, int]) -> float:
        """Return deterministic desirability score for a target cell."""
        cell = self.grid_world.get_cell_values(coord)
        return cell.resource - cell.crime

    def _sync_cell_signals(self) -> None:
        """Mirror global environment signals into localized cell state."""
        for index, agent in enumerate(self.agents):
            coord = self.grid_world.get_agent_cell(str(index))
            if coord is None:
                continue
            occupant_count = max(1, len(self.grid_world.get_occupants(coord)))
            self.grid_world.set_cell_values(
                coord,
                resource=max(0.0, float(self.environment.food_supply / occupant_count)),
                crime=max(0.0, float(self.environment.crime_rate)),
            )

    def _build_grid_world(self, agent_count: int) -> GridWorld:
        """Create a square grid large enough for all managed agents."""
        width = max(1, ceil(sqrt(max(1, agent_count))))
        height = max(1, ceil(max(1, agent_count) / width))
        return GridWorld(width=width, height=height)

    def _agent_environment_state(self) -> dict[str, int]:
        """Translate environment values into signals used by agents."""
        state = self.environment.state()
        return {
            **state,
            "risk": state["crime_rate"],
            "opportunity": max(0, state["food_supply"] - state["price"]),
            "social": max(0, 100 - state["crime_rate"]),
        }

    def _apply_causal_crime_rate(self) -> None:
        """Blend causal crime projection with current crime state."""
        inequality_score = int(round(self._gini() * 100))
        projected_crime = crime_from_price_and_inequality(
            price=self.environment.price,
            inequality=inequality_score,
        )
        self.environment.crime_rate = int(
            round((self.environment.crime_rate + projected_crime) / 2)
        )
        self.environment._clamp_values()

    def _history_entry(self, step_number: int, actions: list[Action]) -> HistoryEntry:
        """Build one raw state-history entry."""
        return {
            "step": step_number,
            "actions": actions,
            "environment": self.environment.state(),
        }

    def _metrics_entry(self, step_number: int) -> MetricsEntry:
        """Build one metrics-over-time entry from current simulation state."""
        crime_history = list(self._crime_history)
        crime_rate = self.environment.crime_rate if crime_history else 0
        return {
            "step": step_number,
            "gini": self._gini(),
            "average_satisfaction": average_satisfaction(self.agents),
            "crime_rate": crime_rate,
            "crime_history": crime_history,
            "food_supply": self.environment.food_supply,
            "price": self.environment.price,
        }

    def _gini(self) -> float:
        """Calculate current wealth inequality across managed agents."""
        return gini_coefficient(agent.wealth for agent in self.agents)


def run_full_simulation(
    steps: int,
    agents: Iterable[Agent],
    environment: Environment,
    director: DirectorAI | None = None,
) -> list[MetricsEntry]:
    """Convenience function for running a fully integrated simulation."""
    simulation = IntegratedSimulation(
        agents=agents,
        environment=environment,
        director=director,
    )
    return simulation.run(steps)
