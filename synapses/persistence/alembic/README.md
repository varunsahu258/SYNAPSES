# Alembic Migrations

This directory stores Alembic migration scripts for PostgreSQL deployments.

- `versions/0001_create_persistence_tables.py` creates run/metric/intervention/config/snapshot/checkpoint tables.
- Indexing focuses on `(run_id, step)` access paths for time-series replay and historical retrieval.
