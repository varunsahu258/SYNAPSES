"""Application service for simulation use-cases."""

from __future__ import annotations

from synapses.ai.director import DirectorAI
from synapses.core.entities import Environment
from synapses.core.engine import IntegratedSimulation
from synapses.experiments import build_agents


class SimulationService:
    """Application-facing service for simulation execution."""

    def build_simulation(self, num_agents: int, tax_rate: float = 0.0) -> IntegratedSimulation:
        """Build a deterministic integrated simulation."""
        return IntegratedSimulation(
            agents=build_agents(num_agents, tax_rate),
            environment=Environment(food_supply=100, price=10, crime_rate=10),
            director=DirectorAI(),
        )

    def run_simulation(self, num_agents: int, steps: int, tax_rate: float = 0.0) -> list[dict[str, object]]:
        """Run a deterministic simulation and return metrics over time."""
        return self.build_simulation(num_agents, tax_rate).run(steps)
