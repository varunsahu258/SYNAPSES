"""FastAPI adapter for SYNAPSES use-cases."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ValidationError

from synapses.application.services import ExperimentService, SimulationService

app = FastAPI(title="SYNAPSES Simulation API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SimulationRequest(BaseModel):
    num_agents: int = Field(..., ge=1)
    steps: int = Field(..., ge=0)
    tax_rate: float = Field(0.0, ge=0.0, le=1.0)


class SimulationResponse(BaseModel):
    metrics_over_time: list[dict[str, Any]]


class ExperimentResponse(BaseModel):
    experiments: dict[str, dict[str, Any]]
    comparison: dict[str, dict[str, Any]]


_simulation_service = SimulationService()
_experiment_service = ExperimentService()


@app.post("/run_simulation", response_model=SimulationResponse)
def run_simulation(request: SimulationRequest) -> SimulationResponse:
    return SimulationResponse(
        metrics_over_time=_simulation_service.run_simulation(
            num_agents=request.num_agents,
            steps=request.steps,
            tax_rate=request.tax_rate,
        )
    )


@app.websocket("/ws/run_simulation")
async def stream_simulation(websocket: WebSocket) -> None:
    await websocket.accept()
    try:
        payload = await websocket.receive_json()
        request = SimulationRequest(**payload)
    except ValidationError as exc:
        await websocket.send_json({"type": "error", "detail": str(exc)})
        await websocket.close(code=1008)
        return

    metrics_over_time: list[dict[str, Any]] = []
    simulation = _simulation_service.build_simulation(
        num_agents=request.num_agents,
        tax_rate=request.tax_rate,
    )
    for metrics in simulation.iter_steps(request.steps):
        metrics_over_time.append(metrics)
        await websocket.send_json({"type": "step", "metrics": metrics})

    await websocket.send_json({"type": "complete", "metrics_over_time": metrics_over_time})
    await websocket.close()


@app.post("/run_experiment", response_model=ExperimentResponse)
def run_experiment_endpoint(request: SimulationRequest) -> ExperimentResponse:
    return ExperimentResponse(
        **_experiment_service.run_experiment(
            num_agents=request.num_agents,
            steps=request.steps,
            tax_rate=request.tax_rate,
        )
    )
