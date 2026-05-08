"""Tests for advanced experiment orchestration framework."""

from __future__ import annotations

import json
from pathlib import Path

from synapses.experiments import (
    ExperimentRunner,
    ExperimentSpec,
    aggregate_runs,
    build_comparison_report,
    build_plot_series,
    export_records_csv,
    export_records_json,
    parameter_sweep_grid,
)


def _fake_runner(params: dict[str, object]) -> dict[str, float]:
    seed = int(params["seed"])
    alpha = float(params.get("alpha", 1.0))
    if params.get("fail_once") and seed % 2 == 0:
        raise RuntimeError("synthetic failure")
    return {
        "stability": 100.0 + alpha - (seed % 5),
        "inequality": 30.0 - alpha + (seed % 3),
    }


def test_parameter_sweep_grid_generates_cartesian_product() -> None:
    combos = parameter_sweep_grid({"alpha": [0.1, 0.2], "beta": [1, 2, 3]})
    assert len(combos) == 6
    assert {c["alpha"] for c in combos} == {0.1, 0.2}


def test_batch_runner_and_aggregation_and_reports(tmp_path: Path) -> None:
    specs = [
        ExperimentSpec(experiment_id="exp-a", parameters={"alpha": 0.1}, seed=100),
        ExperimentSpec(experiment_id="exp-b", parameters={"alpha": 0.5}, seed=200),
    ]
    runner = ExperimentRunner(_fake_runner)
    records = runner.run_batch(specs, runs_per_spec=4, max_workers=2)
    assert len(records) == 8

    summaries = aggregate_runs(records)
    assert len(summaries) == 2
    assert all(summary.successful_runs == 4 for summary in summaries)
    assert all("stability" in summary.metrics for summary in summaries)

    report = build_comparison_report(summaries)
    assert len(report["experiments"]) == 2

    series = build_plot_series(summaries, metric="stability")
    assert len(series["x"]) == 2
    assert len(series["yerr"]) == 2

    json_path = export_records_json(records, tmp_path / "records.json")
    csv_path = export_records_csv(records, tmp_path / "records.csv")
    assert json_path.exists() and csv_path.exists()
    parsed = json.loads(json_path.read_text(encoding="utf-8"))
    assert len(parsed) == 8


def test_failure_recovery_retries() -> None:
    specs = [ExperimentSpec(experiment_id="exp-retry", parameters={"alpha": 0.2, "fail_once": True}, seed=10)]
    runner = ExperimentRunner(_fake_runner)
    records = runner.run_batch(specs, runs_per_spec=2, retry_failures=1)
    assert len(records) == 2
    # deterministic setup still fails even after retry for one run seed.
    assert any(not record.success for record in records)
