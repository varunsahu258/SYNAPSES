"""Experiment framework package.

This package currently re-exports existing experiment helpers from the legacy
module to preserve backward compatibility during incremental refactor.
"""

from synapses.experiments.counterfactual import CounterfactualBranch, CounterfactualEngine, WorldSnapshot
from synapses.experiments.orchestration import (
    AggregateMetric,
    ExperimentRunRecord,
    ExperimentRunner,
    ExperimentSpec,
    ExperimentSummary,
    aggregate_runs,
    build_comparison_report,
    build_plot_series,
    export_records_csv,
    export_records_json,
    parameter_sweep_grid,
)
from synapses.experiments_legacy import NoDirector, RandomDirector, build_agents, run_experiment

__all__ = [
    "NoDirector",
    "RandomDirector",
    "build_agents",
    "run_experiment",
    "CounterfactualBranch",
    "CounterfactualEngine",
    "WorldSnapshot",
    "AggregateMetric",
    "ExperimentRunRecord",
    "ExperimentRunner",
    "ExperimentSpec",
    "ExperimentSummary",
    "aggregate_runs",
    "build_comparison_report",
    "build_plot_series",
    "export_records_csv",
    "export_records_json",
    "parameter_sweep_grid",
]
