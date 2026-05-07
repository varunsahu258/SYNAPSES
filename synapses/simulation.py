"""Simulation engine for coordinating agents and an environment.

The engine is intentionally deterministic: each step reads the current
environment, asks every agent for one action, applies those actions to the
environment, and stores a serializable history entry.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping

from .agent import Agent
from .environment import Environment

Action = dict[str, str]
HistoryEntry = dict[str, Any]


@dataclass
class SimulationEngine:
    """Run deterministic simulations across agents and one environment.

    Attributes:
        agents: Managed agents that act once per simulation step.
        environment: Environment updated from agent action dictionaries.
    """

    agents: list[Agent] = field(default_factory=list)
    environment: Environment = field(default_factory=Environment)

    def __init__(
        self,
        agents: Iterable[Agent] | None = None,
        environment: Environment | None = None,
    ) -> None:
        """Create an engine with optional agents and environment."""
        self.agents = list(agents or [])
        self.environment = environment or Environment()

    def add_agent(self, agent: Agent) -> None:
        """Register one agent for future simulation steps."""
        self.agents.append(agent)

    def run(self, steps: int) -> list[HistoryEntry]:
        """Run the simulation loop for ``steps`` iterations.

        Args:
            steps: Number of simulation steps to run. Must be zero or greater.

        Returns:
            State history with one entry per completed step.
        """
        if steps < 0:
            raise ValueError("Simulation steps must be zero or greater.")

        history: list[HistoryEntry] = []
        for step_number in range(1, steps + 1):
            history.append(self._run_step(step_number))

        return history

    def _run_step(self, step_number: int) -> HistoryEntry:
        """Run one simulation step and return its history entry."""
        environment_state = self._agent_environment_state()
        actions = self._collect_actions(environment_state)
        updated_environment = self.environment.update(actions)

        return {
            "step": step_number,
            "actions": actions,
            "environment": updated_environment,
        }

    def _collect_actions(self, environment_state: Mapping[str, Any]) -> list[Action]:
        """Ask every managed agent for an action dictionary."""
        return [agent.act(environment_state) for agent in self.agents]

    def _agent_environment_state(self) -> dict[str, int]:
        """Translate environment variables into signals agents understand."""
        state = self.environment.state()
        return {
            **state,
            "risk": state["crime_rate"],
            "opportunity": max(0, state["food_supply"] - state["price"]),
            "social": max(0, 100 - state["crime_rate"]),
        }
