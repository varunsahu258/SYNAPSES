"""Utilities for building small, testable SYNAPSES simulation primitives."""

from .agent import Agent
from .causal import crime_from_price_and_inequality, price_from_food_supply
from .director import DirectorAI
from .environment import Environment
from .experiments import (
    CounterfactualBranch,
    CounterfactualEngine,
    NoDirector,
    RandomDirector,
    WorldSnapshot,
    AggregateMetric,
    ExperimentRunRecord,
    ExperimentRunner,
    ExperimentSpec,
    ExperimentSummary,
    build_agents,
    run_experiment,
    aggregate_runs,
    build_comparison_report,
    build_plot_series,
    export_records_csv,
    export_records_json,
    parameter_sweep_grid,
)
from .integration import IntegratedSimulation, run_full_simulation
from .metrics import average_satisfaction, gini_coefficient, track_crime
try:
    from .persistence import DatabaseSettings, PersistenceService, ReproducibilityRecord
except Exception:  # pragma: no cover
    DatabaseSettings = PersistenceService = ReproducibilityRecord = None
from .simulation import AgentSignalConfig, SimulationEngine
from .workflow import Workflow, WorkflowStep, create_default_workflow

__all__ = [
    "parameter_sweep_grid",
    "export_records_json",
    "export_records_csv",
    "build_plot_series",
    "build_comparison_report",
    "aggregate_runs",
    "ExperimentSummary",
    "ExperimentSpec",
    "ExperimentRunner",
    "ExperimentRunRecord",
    "AggregateMetric",
    "Agent",
    "average_satisfaction",
    "crime_from_price_and_inequality",
    "DirectorAI",
    "CounterfactualBranch",
    "CounterfactualEngine",
    "Environment",
    "build_agents",
    "NoDirector",
    "gini_coefficient",
    "IntegratedSimulation",
    "AgentSignalConfig",
    "SimulationEngine",
    "price_from_food_supply",
    "run_experiment",
    "run_full_simulation",
    "RandomDirector",
    "run_full_simulation",
    "track_crime",
    "WorldSnapshot",
    "DatabaseSettings",
    "PersistenceService",
    "ReproducibilityRecord",
    "Workflow",
    "WorkflowStep",
    "create_default_workflow",
]
