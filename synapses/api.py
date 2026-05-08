"""Backward-compatible API module.

This module re-exports the FastAPI app from the new interfaces layer.
"""

from synapses.interfaces.api.fastapi_app import (
    ExperimentResponse,
    SimulationRequest,
    SimulationResponse,
    app,
    run_experiment_endpoint,
    run_simulation,
    stream_simulation,
)

__all__ = [
    "app",
    "SimulationRequest",
    "SimulationResponse",
    "ExperimentResponse",
    "run_simulation",
    "stream_simulation",
    "run_experiment_endpoint",
]
