"""Adapter that wraps trained RL director models behind recommend()."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .observation_bridge import metrics_to_observation


class RLDirectorAdapter:
    """Policy adapter compatible with IntegratedSimulation director interface."""

    def __init__(self, model_path: str | Path):
        from stable_baselines3 import PPO

        self._model = PPO.load(str(model_path))

    def recommend(self, global_metrics: dict[str, Any] | None) -> list[dict[str, str]]:
        obs = metrics_to_observation(global_metrics).as_array()
        action, _ = self._model.predict(obs, deterministic=True)
        action_values = [float(v) for v in list(action)]
        return [self._map_action(action_values)]

    def _map_action(self, action_values: list[float]) -> dict[str, str]:
        taxation, subsidies, policing, welfare_allocation, _zoning, _distribution = action_values
        if policing > 0.4:
            return {"action": "increase_safety_programs", "reason": "rl_policy"}
        if welfare_allocation > 0.3 or subsidies > 0.3:
            return {"action": "fund_public_services", "reason": "rl_policy"}
        if taxation > 0.3:
            return {"action": "redistribute_resources", "reason": "rl_policy"}
        return {"action": "monitor", "reason": "rl_policy"}
