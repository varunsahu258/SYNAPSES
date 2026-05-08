"""FastAPI adapter for SYNAPSES use-cases."""

from __future__ import annotations

from typing import Any
from pathlib import Path

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ValidationError

from synapses.application.services import ExperimentService, SimulationService
from synapses.director import DirectorAI
from synapses.environment import Environment
from synapses.experiments import (
    CounterfactualEngine,
    ExperimentRunRecord,
    ExperimentRunner,
    ExperimentSpec,
    aggregate_runs,
    build_comparison_report,
    export_records_csv,
    parameter_sweep_grid,
)
from synapses.experiments_legacy import build_agents

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
    gini_threshold: float = Field(0.4, ge=0.0, le=1.0)
    satisfaction_threshold: float = Field(40.0, ge=0.0, le=100.0)
    crime_threshold: float = Field(50.0, ge=0.0, le=100.0)


class SimulationResponse(BaseModel):
    metrics_over_time: list[dict[str, Any]]
    grid_state: dict[str, Any]


class ExperimentResponse(BaseModel):
    experiments: dict[str, dict[str, Any]]
    comparison: dict[str, dict[str, Any]]


class SweepRequest(BaseModel):
    num_agents: list[int] = Field(default_factory=lambda: [2, 4, 8])
    steps: list[int] = Field(default_factory=lambda: [5, 10])
    tax_rate: list[float] = Field(default_factory=lambda: [0.0, 0.25])
    runs_per_spec: int = Field(2, ge=1, le=50)


class CounterfactualRequest(BaseModel):
    num_agents: int = Field(..., ge=1)
    steps: int = Field(..., ge=0)
    tax_rate: float = Field(0.0, ge=0.0, le=1.0)


_simulation_service = SimulationService()
_experiment_service = ExperimentService()


def _spatial_state(simulation: Any) -> dict[str, Any]:
    world = simulation.grid_world
    agents = [
        {"agent_id": str(index), "position": list(agent.position)}
        for index, agent in enumerate(simulation.agents)
    ]
    cells = [
        {"coord": list(coord), "resource": cell.resource, "crime": cell.crime}
        for coord, cell in world._cells.items()
    ]
    return {
        "width": world.width,
        "height": world.height,
        "cell_size": world.cell_size,
        "agents": agents,
        "cells": cells,
    }


def _build_director(request: SimulationRequest) -> DirectorAI:
    return DirectorAI(
        gini_threshold=request.gini_threshold,
        satisfaction_threshold=request.satisfaction_threshold,
        crime_threshold=request.crime_threshold,
    )


def _build_simulation(request: SimulationRequest) -> Any:
    simulation = _simulation_service.build_simulation(
        num_agents=request.num_agents,
        tax_rate=request.tax_rate,
    )
    simulation.director = _build_director(request)
    return simulation


@app.post("/run_simulation", response_model=SimulationResponse)
def run_simulation(request: SimulationRequest) -> SimulationResponse:
    simulation = _build_simulation(request)
    metrics = simulation.run(request.steps)
    return SimulationResponse(
        metrics_over_time=metrics,
        grid_state=_spatial_state(simulation),
    )


@app.post("/grid_state")
def get_grid_state(request: SimulationRequest) -> dict[str, Any]:
    simulation = _build_simulation(request)
    simulation.run(request.steps)
    return _spatial_state(simulation)


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
    simulation = _build_simulation(request)
    for metrics in simulation.iter_steps(request.steps):
        metrics_over_time.append(metrics)
        await websocket.send_json(
            {"type": "step", "metrics": metrics, "spatial": _spatial_state(simulation)}
        )

    await websocket.send_json(
        {
            "type": "complete",
            "metrics_over_time": metrics_over_time,
            "spatial": _spatial_state(simulation),
        }
    )
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


@app.post("/experiments/parameter_sweep")
def run_parameter_sweep(request: SweepRequest) -> dict[str, Any]:
    grid = parameter_sweep_grid(
        {
            "num_agents": request.num_agents,
            "steps": request.steps,
            "tax_rate": request.tax_rate,
        }
    )
    specs = [
        ExperimentSpec(experiment_id=f"sweep_{idx}", parameters=params, seed=42 + idx)
        for idx, params in enumerate(grid)
    ]

    runner = ExperimentRunner(
        lambda params: _experiment_service.run_experiment(
            num_agents=int(params["num_agents"]),
            steps=int(params["steps"]),
            tax_rate=float(params["tax_rate"]),
        )["comparison"]["director_based"]
    )
    records: list[ExperimentRunRecord] = runner.run_batch(specs, request.runs_per_spec)
    summaries = aggregate_runs(records)
    report = build_comparison_report(summaries)
    Path("artifacts").mkdir(parents=True, exist_ok=True)
    csv_path = export_records_csv(records, "artifacts/parameter_sweep.csv")
    return {"report": report, "csv_path": str(csv_path), "records": len(records)}


@app.post("/counterfactual/run")
def run_counterfactual(request: CounterfactualRequest) -> dict[str, Any]:
    agents = build_agents(request.num_agents, request.tax_rate)
    engine = CounterfactualEngine(base_agents=agents, base_environment=Environment())
    baseline = engine.create_branch("baseline")
    policy = engine.create_branch("policy")
    policy.add_intervention(1, lambda env, _agents, _rng: setattr(env, "food_supply", env.food_supply + 10))
    engine.run_all(request.steps)
    return {
        "baseline_steps": len(baseline.metrics()),
        "policy_steps": len(policy.metrics()),
        "comparison": engine.compare("baseline"),
    }
