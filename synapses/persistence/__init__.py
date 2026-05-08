"""Persistence layer for experiment reproducibility and historical retrieval."""

from .db import DatabaseSettings, build_engine, build_session_factory

try:
    from .models import (
        Base,
        ExperimentConfigVersion,
        InterventionRecord,
        ModelCheckpoint,
        RunMetric,
        SimulationRun,
        SnapshotRecord,
    )
    from .service import PersistenceService, ReproducibilityRecord
except Exception:  # pragma: no cover
    Base = ExperimentConfigVersion = InterventionRecord = ModelCheckpoint = None
    RunMetric = SimulationRun = SnapshotRecord = None
    PersistenceService = ReproducibilityRecord = None

__all__ = [
    "Base",
    "DatabaseSettings",
    "build_engine",
    "build_session_factory",
    "SimulationRun",
    "RunMetric",
    "InterventionRecord",
    "ExperimentConfigVersion",
    "SnapshotRecord",
    "ModelCheckpoint",
    "PersistenceService",
    "ReproducibilityRecord",
]
