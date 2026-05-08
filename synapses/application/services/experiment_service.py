"""Application service for experiment use-cases."""

from __future__ import annotations

from typing import Any

from synapses.experiments import run_experiment


class ExperimentService:
    """Application-facing wrapper around experiment orchestration."""

    def run_experiment(self, num_agents: int, steps: int, tax_rate: float = 0.0) -> dict[str, dict[str, Any]]:
        """Run all experiment variants and return comparison output."""
        return run_experiment(num_agents=num_agents, steps=steps, tax_rate=tax_rate)
