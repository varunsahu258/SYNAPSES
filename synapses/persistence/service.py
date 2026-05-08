"""Persistence services for simulation records and deterministic replay."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from .models import (
    ExperimentConfigVersion,
    InterventionRecord,
    ModelCheckpoint,
    RunMetric,
    SimulationRun,
    SnapshotRecord,
)


@dataclass(frozen=True)
class ReproducibilityRecord:
    """Stable metadata required to reproduce a run."""

    run_uid: str
    seed: int
    config_version: str
    config_hash: str


class PersistenceService:
    """Repository-style persistence API decoupled from simulation internals."""

    def __init__(self, session: Any) -> None:
        self._session = session

    def create_run(self, *, run_uid: str, experiment_name: str, seed: int, config_version: str) -> SimulationRun:
        run = SimulationRun(
            run_uid=run_uid,
            experiment_name=experiment_name,
            seed=seed,
            status="running",
            started_at=datetime.now(timezone.utc),
            config_version=config_version,
        )
        self._session.add(run)
        self._session.flush()
        return run

    def finalize_run(self, run_id: int, status: str) -> None:
        run = self._session.get(SimulationRun, run_id)
        if run is None:
            raise ValueError(f"unknown run id: {run_id}")
        run.status = status
        run.finished_at = datetime.now(timezone.utc)

    def store_metric(self, run_id: int, step: int, key: str, value: float) -> None:
        self._session.add(RunMetric(run_id=run_id, step=step, key=key, value=value))

    def store_intervention(self, run_id: int, step: int, intervention_type: str, payload: dict[str, Any]) -> None:
        self._session.add(
            InterventionRecord(
                run_id=run_id,
                step=step,
                intervention_type=intervention_type,
                payload=payload,
            )
        )

    def store_config_version(self, experiment_name: str, version: str, config: dict[str, Any]) -> ExperimentConfigVersion:
        content = json.dumps(config, sort_keys=True, separators=(",", ":")).encode("utf-8")
        content_hash = hashlib.sha256(content).hexdigest()
        record = ExperimentConfigVersion(
            experiment_name=experiment_name,
            version=version,
            config=config,
            content_hash=content_hash,
            created_at=datetime.now(timezone.utc),
        )
        self._session.add(record)
        self._session.flush()
        return record

    def store_snapshot(self, run_id: int, step: int, state_blob: bytes, state_format: str = "json") -> None:
        self._session.add(
            SnapshotRecord(run_id=run_id, step=step, state_blob=state_blob, state_format=state_format)
        )

    def store_model_checkpoint(
        self,
        run_id: int,
        step: int,
        model_name: str,
        *,
        storage_uri: str | None,
        payload: bytes | None,
    ) -> None:
        self._session.add(
            ModelCheckpoint(
                run_id=run_id,
                step=step,
                model_name=model_name,
                storage_uri=storage_uri,
                payload=payload,
            )
        )

    def build_reproducibility_record(self, run_uid: str) -> ReproducibilityRecord:
        run = self._session.query(SimulationRun).filter_by(run_uid=run_uid).one()
        cfg = (
            self._session.query(ExperimentConfigVersion)
            .filter_by(experiment_name=run.experiment_name, version=run.config_version)
            .one()
        )
        return ReproducibilityRecord(
            run_uid=run_uid,
            seed=run.seed,
            config_version=run.config_version,
            config_hash=cfg.content_hash,
        )
