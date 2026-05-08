"""SQLAlchemy ORM models for simulation persistence and reproducibility."""

from __future__ import annotations

from datetime import datetime
from typing import Any

try:
    from sqlalchemy import (
        JSON,
        DateTime,
        Float,
        ForeignKey,
        Index,
        Integer,
        LargeBinary,
        String,
        Text,
        UniqueConstraint,
    )
    from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
except ModuleNotFoundError as exc:  # pragma: no cover
    _SQLALCHEMY_IMPORT_ERROR = exc

    class DeclarativeBase:  # type: ignore[override]
        pass

    Mapped = Any  # type: ignore[assignment]
    JSON = DateTime = Float = ForeignKey = Index = Integer = LargeBinary = String = Text = UniqueConstraint = object
    def relationship(*args: Any, **kwargs: Any) -> Any:  # noqa: ANN401
        return None

    def mapped_column(*args: Any, **kwargs: Any) -> Any:  # noqa: ANN401
        return None

else:
    _SQLALCHEMY_IMPORT_ERROR = None


class Base(DeclarativeBase):
    """Declarative ORM base."""


class SimulationRun(Base):
    """Top-level simulation execution record."""

    __tablename__ = "simulation_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_uid: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    experiment_name: Mapped[str] = mapped_column(String(128), nullable=False)
    seed: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    config_version: Mapped[str] = mapped_column(String(64), nullable=False)

    metrics = relationship("RunMetric", back_populates="run", cascade="all, delete-orphan")


class RunMetric(Base):
    """Time-series metric snapshots associated with a run."""

    __tablename__ = "run_metrics"
    __table_args__ = (Index("ix_run_metrics_run_step", "run_id", "step"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("simulation_runs.id", ondelete="CASCADE"))
    step: Mapped[int] = mapped_column(Integer, nullable=False)
    key: Mapped[str] = mapped_column(String(64), nullable=False)
    value: Mapped[float] = mapped_column(Float, nullable=False)

    run = relationship("SimulationRun", back_populates="metrics")


class InterventionRecord(Base):
    """Director and operator interventions applied during a run."""

    __tablename__ = "interventions"
    __table_args__ = (Index("ix_interventions_run_step", "run_id", "step"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("simulation_runs.id", ondelete="CASCADE"))
    step: Mapped[int] = mapped_column(Integer, nullable=False)
    intervention_type: Mapped[str] = mapped_column(String(64), nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)


class ExperimentConfigVersion(Base):
    """Versioned experiment configuration snapshots."""

    __tablename__ = "experiment_configs"
    __table_args__ = (
        UniqueConstraint("experiment_name", "version", name="uq_experiment_name_version"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    experiment_name: Mapped[str] = mapped_column(String(128), nullable=False)
    version: Mapped[str] = mapped_column(String(64), nullable=False)
    config: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class SnapshotRecord(Base):
    """State snapshot reference for replay/recovery."""

    __tablename__ = "snapshots"
    __table_args__ = (Index("ix_snapshots_run_step", "run_id", "step", unique=True),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("simulation_runs.id", ondelete="CASCADE"))
    step: Mapped[int] = mapped_column(Integer, nullable=False)
    state_blob: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    state_format: Mapped[str] = mapped_column(String(16), default="json", nullable=False)


class ModelCheckpoint(Base):
    """Serialized model checkpoint metadata and binary payload."""

    __tablename__ = "model_checkpoints"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("simulation_runs.id", ondelete="CASCADE"))
    step: Mapped[int] = mapped_column(Integer, nullable=False)
    model_name: Mapped[str] = mapped_column(String(64), nullable=False)
    storage_uri: Mapped[str | None] = mapped_column(Text, nullable=True)
    payload: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
