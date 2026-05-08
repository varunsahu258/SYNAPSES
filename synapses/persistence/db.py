"""Database engine/session helpers for persistence services."""

from __future__ import annotations

from dataclasses import dataclass

try:
    from sqlalchemy import create_engine
    from sqlalchemy.engine import Engine
    from sqlalchemy.orm import Session, sessionmaker
except ModuleNotFoundError as exc:  # pragma: no cover
    create_engine = None  # type: ignore[assignment]
    Engine = object  # type: ignore[assignment,misc]
    Session = object  # type: ignore[assignment,misc]
    sessionmaker = None  # type: ignore[assignment]
    _SQLALCHEMY_IMPORT_ERROR = exc
else:
    _SQLALCHEMY_IMPORT_ERROR = None


@dataclass(frozen=True)
class DatabaseSettings:
    """Configuration for SQLAlchemy engine creation.

    The URL is injectable so callers can use PostgreSQL in production and
    SQLite for local tests.
    """

    url: str
    echo: bool = False
    pool_pre_ping: bool = True


def _require_sqlalchemy() -> None:
    if _SQLALCHEMY_IMPORT_ERROR is not None:
        raise ModuleNotFoundError(
            "sqlalchemy is required for persistence features"
        ) from _SQLALCHEMY_IMPORT_ERROR


def build_engine(settings: DatabaseSettings) -> Engine:
    """Build an SQLAlchemy engine for the configured backend."""

    _require_sqlalchemy()
    return create_engine(
        settings.url,
        echo=settings.echo,
        pool_pre_ping=settings.pool_pre_ping,
        future=True,
    )


def build_session_factory(engine: Engine) -> sessionmaker[Session]:
    """Build a typed session factory bound to ``engine``."""

    _require_sqlalchemy()
    return sessionmaker(bind=engine, expire_on_commit=False, class_=Session)
