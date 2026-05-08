"""Advanced experiment orchestration for large-scale simulation research.

This module is intentionally UI-agnostic and transport-agnostic. It provides
building blocks for Monte Carlo runs, parameter sweeps, batch execution,
reproducibility metadata, exports, and aggregate statistics.
"""

from __future__ import annotations

import csv
import itertools
import json
import math
import random
from concurrent.futures import FIRST_COMPLETED, Future, ProcessPoolExecutor, ThreadPoolExecutor, wait
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from statistics import mean, pstdev
from typing import Any, Callable, Iterable, Mapping


SimulationRunner = Callable[[Mapping[str, Any]], Mapping[str, float]]


@dataclass(frozen=True)
class ExperimentSpec:
    """Defines a single experiment run configuration."""

    experiment_id: str
    parameters: dict[str, Any]
    seed: int
    tags: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class ExperimentRunRecord:
    """Result record for an executed run."""

    experiment_id: str
    run_index: int
    seed: int
    parameters: dict[str, Any]
    metrics: dict[str, float]
    success: bool
    error: str | None = None


@dataclass(frozen=True)
class AggregateMetric:
    """Aggregate statistics for one metric across runs."""

    count: int
    mean: float
    std_dev: float
    min_value: float
    max_value: float
    ci95_low: float
    ci95_high: float


@dataclass(frozen=True)
class ExperimentSummary:
    """Aggregate summary + metadata for a completed batch."""

    experiment_id: str
    parameters: dict[str, Any]
    metrics: dict[str, AggregateMetric]
    successful_runs: int
    failed_runs: int
    reproducibility: dict[str, Any]


def parameter_sweep_grid(grid: Mapping[str, Iterable[Any]]) -> list[dict[str, Any]]:
    """Return cartesian product of parameter values for sweep experiments."""
    keys = list(grid.keys())
    values = [list(grid[key]) for key in keys]
    return [dict(zip(keys, combination, strict=True)) for combination in itertools.product(*values)]


def _execute_single(spec: ExperimentSpec, run_index: int, runner: SimulationRunner) -> ExperimentRunRecord:
    """Execute one simulation run with deterministic seed handling."""
    seeded_params = dict(spec.parameters)
    seeded_params["seed"] = spec.seed + run_index
    random.seed(seeded_params["seed"])
    try:
        metrics = dict(runner(seeded_params))
        return ExperimentRunRecord(
            experiment_id=spec.experiment_id,
            run_index=run_index,
            seed=seeded_params["seed"],
            parameters=spec.parameters,
            metrics={k: float(v) for k, v in metrics.items()},
            success=True,
        )
    except Exception as exc:  # failure recovery path
        return ExperimentRunRecord(
            experiment_id=spec.experiment_id,
            run_index=run_index,
            seed=seeded_params["seed"],
            parameters=spec.parameters,
            metrics={},
            success=False,
            error=str(exc),
        )


class ExperimentRunner:
    """Runs experiment queues with optional parallel execution and retries."""

    def __init__(self, runner: SimulationRunner) -> None:
        self._runner = runner

    def run_batch(
        self,
        specs: list[ExperimentSpec],
        runs_per_spec: int,
        *,
        max_workers: int = 1,
        use_processes: bool = False,
        retry_failures: int = 0,
    ) -> list[ExperimentRunRecord]:
        """Execute many experiments using queue-style scheduling."""
        if runs_per_spec < 1:
            raise ValueError("runs_per_spec must be at least 1")
        queue: list[tuple[ExperimentSpec, int, int]] = [
            (spec, run_idx, 0)
            for spec in specs
            for run_idx in range(runs_per_spec)
        ]
        records: list[ExperimentRunRecord] = []
        if max_workers <= 1:
            while queue:
                spec, run_idx, attempt = queue.pop(0)
                record = _execute_single(spec, run_idx, self._runner)
                if (not record.success) and attempt < retry_failures:
                    queue.append((spec, run_idx, attempt + 1))
                else:
                    records.append(record)
            return records

        executor_cls = ProcessPoolExecutor if use_processes else ThreadPoolExecutor
        with executor_cls(max_workers=max_workers) as executor:
            futures: dict[Future[ExperimentRunRecord], tuple[ExperimentSpec, int, int]] = {}
            while queue or futures:
                while queue and len(futures) < max_workers:
                    spec, run_idx, attempt = queue.pop(0)
                    future = executor.submit(_execute_single, spec, run_idx, self._runner)
                    futures[future] = (spec, run_idx, attempt)
                done, _ = wait(futures.keys(), return_when=FIRST_COMPLETED)
                for future in done:
                    spec, run_idx, attempt = futures.pop(future)
                    record = future.result()
                    if (not record.success) and attempt < retry_failures:
                        queue.append((spec, run_idx, attempt + 1))
                    else:
                        records.append(record)
        return records


def aggregate_runs(records: list[ExperimentRunRecord]) -> list[ExperimentSummary]:
    """Aggregate run records into per-experiment summaries."""
    grouped: dict[str, list[ExperimentRunRecord]] = {}
    for record in records:
        grouped.setdefault(record.experiment_id, []).append(record)

    summaries: list[ExperimentSummary] = []
    for exp_id, exp_records in grouped.items():
        successful = [r for r in exp_records if r.success]
        failed = [r for r in exp_records if not r.success]
        params = exp_records[0].parameters
        metric_names = sorted({k for r in successful for k in r.metrics})
        metric_summary = {
            name: _aggregate_metric([r.metrics[name] for r in successful if name in r.metrics])
            for name in metric_names
        }
        reproducibility = {
            "seeds": [r.seed for r in exp_records],
            "generated_at_utc": datetime.now(UTC).isoformat(),
            "total_runs": len(exp_records),
        }
        summaries.append(
            ExperimentSummary(
                experiment_id=exp_id,
                parameters=params,
                metrics=metric_summary,
                successful_runs=len(successful),
                failed_runs=len(failed),
                reproducibility=reproducibility,
            )
        )
    return summaries


def _aggregate_metric(values: list[float]) -> AggregateMetric:
    if not values:
        return AggregateMetric(0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    n = len(values)
    mu = mean(values)
    sigma = pstdev(values) if n > 1 else 0.0
    margin = 1.96 * (sigma / math.sqrt(n)) if n > 1 else 0.0
    return AggregateMetric(
        count=n,
        mean=mu,
        std_dev=sigma,
        min_value=min(values),
        max_value=max(values),
        ci95_low=mu - margin,
        ci95_high=mu + margin,
    )


def export_records_json(records: list[ExperimentRunRecord], path: str | Path) -> Path:
    out = Path(path)
    out.write_text(json.dumps([asdict(r) for r in records], indent=2), encoding="utf-8")
    return out


def export_records_csv(records: list[ExperimentRunRecord], path: str | Path) -> Path:
    out = Path(path)
    metric_keys = sorted({k for r in records for k in r.metrics})
    with out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["experiment_id", "run_index", "seed", "success", "error", *metric_keys, "parameters_json"])
        for record in records:
            writer.writerow([
                record.experiment_id,
                record.run_index,
                record.seed,
                record.success,
                record.error or "",
                *[record.metrics.get(k, "") for k in metric_keys],
                json.dumps(record.parameters, sort_keys=True),
            ])
    return out


def build_comparison_report(summaries: list[ExperimentSummary]) -> dict[str, Any]:
    """Create machine-readable cross-experiment comparison output."""
    return {
        "experiments": [
            {
                "experiment_id": s.experiment_id,
                "parameters": s.parameters,
                "successful_runs": s.successful_runs,
                "failed_runs": s.failed_runs,
                "metrics": {k: asdict(v) for k, v in s.metrics.items()},
                "reproducibility": s.reproducibility,
            }
            for s in summaries
        ]
    }


def build_plot_series(summaries: list[ExperimentSummary], metric: str) -> dict[str, list[Any]]:
    """Return x/y/error arrays consumable by plotting libraries."""
    x = [s.experiment_id for s in summaries]
    y = [s.metrics[metric].mean if metric in s.metrics else 0.0 for s in summaries]
    err = [s.metrics[metric].ci95_high - y[idx] if metric in s.metrics else 0.0 for idx, s in enumerate(summaries)]
    return {"x": x, "y": y, "yerr": err, "metric": [metric] * len(x)}
