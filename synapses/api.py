"""FastAPI application for running SYNAPSES simulations.

The API layer is intentionally thin: it validates request JSON, builds small
deterministic simulation scenarios, delegates execution to the existing
integration functions, and returns metrics over time or experiment comparisons.
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ValidationError

from .director import DirectorAI
from .environment import Environment
from .experiments import build_agents, run_experiment
from .integration import IntegratedSimulation

app = FastAPI(title="SYNAPSES Simulation API", version="0.1.0")

# Development CORS policy: allow any frontend origin to call the API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SimulationRequest(BaseModel):
    """Request body for running a deterministic SYNAPSES simulation."""

    num_agents: int = Field(..., ge=1, description="Number of agents to create.")
    steps: int = Field(..., ge=0, description="Number of simulation steps to run.")
    tax_rate: float = Field(
        0.0,
        ge=0.0,
        le=1.0,
        description="Optional redistribution rate applied to initial wealth.",
    )


class SimulationResponse(BaseModel):
    """Response body containing metrics over time."""

    metrics_over_time: list[dict[str, Any]]


class ExperimentResponse(BaseModel):
    """Response body containing experiment comparison results."""

    experiments: dict[str, dict[str, Any]]
    comparison: dict[str, dict[str, Any]]


def _build_simulation(request: SimulationRequest) -> IntegratedSimulation:
    """Build a deterministic integrated simulation from request values."""
    return IntegratedSimulation(
        agents=build_agents(request.num_agents, request.tax_rate),
        environment=Environment(food_supply=100, price=10, crime_rate=10),
        director=DirectorAI(),
    )


@app.post("/run_simulation", response_model=SimulationResponse)
def run_simulation(request: SimulationRequest) -> SimulationResponse:
    """Run an integrated simulation and return metrics over time."""
    metrics_over_time = _build_simulation(request).run(request.steps)
    return SimulationResponse(metrics_over_time=metrics_over_time)


@app.websocket("/ws/run_simulation")
async def stream_simulation(websocket: WebSocket) -> None:
    """Stream simulation metrics one step at a time over a WebSocket.

    The client must send one JSON message matching :class:`SimulationRequest`
    immediately after connecting. The server then sends one ``step`` message per
    completed simulation step followed by a final ``complete`` message.
    """
    await websocket.accept()

    try:
        payload = await websocket.receive_json()
        request = SimulationRequest(**payload)
    except ValidationError as exc:
        await websocket.send_json({"type": "error", "detail": str(exc)})
        await websocket.close(code=1008)
        return

    metrics_over_time: list[dict[str, Any]] = []
    for metrics in _build_simulation(request).iter_steps(request.steps):
        metrics_over_time.append(metrics)
        await websocket.send_json({"type": "step", "metrics": metrics})

    await websocket.send_json(
        {"type": "complete", "metrics_over_time": metrics_over_time}
    )
    await websocket.close()


@app.post("/run_experiment", response_model=ExperimentResponse)
def run_experiment_endpoint(request: SimulationRequest) -> ExperimentResponse:
    """Run no-director, random, and director-based variants for comparison."""
    result = run_experiment(
        num_agents=request.num_agents,
        steps=request.steps,
        tax_rate=request.tax_rate,
    )
    return ExperimentResponse(**result)
