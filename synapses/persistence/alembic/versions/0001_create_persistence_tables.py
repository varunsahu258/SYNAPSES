"""create persistence tables

Revision ID: 0001
Revises:
Create Date: 2026-05-08
"""

from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "simulation_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("run_uid", sa.String(length=64), nullable=False, unique=True),
        sa.Column("experiment_name", sa.String(length=128), nullable=False),
        sa.Column("seed", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("config_version", sa.String(length=64), nullable=False),
    )
    op.create_table(
        "run_metrics",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("run_id", sa.Integer(), sa.ForeignKey("simulation_runs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("step", sa.Integer(), nullable=False),
        sa.Column("key", sa.String(length=64), nullable=False),
        sa.Column("value", sa.Float(), nullable=False),
    )
    op.create_index("ix_run_metrics_run_step", "run_metrics", ["run_id", "step"])


def downgrade() -> None:
    op.drop_index("ix_run_metrics_run_step", table_name="run_metrics")
    op.drop_table("run_metrics")
    op.drop_table("simulation_runs")
