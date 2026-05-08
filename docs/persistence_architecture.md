# Persistence and Reproducibility Architecture

## Schema overview

- `simulation_runs`: one record per simulation execution with seed/config version metadata.
- `run_metrics`: step-indexed metric time series for historical retrieval.
- `interventions`: step-indexed intervention payloads for policy tracing.
- `experiment_configs`: immutable, versioned configuration snapshots with SHA-256 hash.
- `snapshots`: binary state snapshots for replay/recovery at selected steps.
- `model_checkpoints`: optional external URI and/or in-DB bytes for trained models.

## Indexing strategy

- Composite indexes on `(run_id, step)` for metrics, interventions, and snapshots.
- Unique constraint on `(experiment_name, version)` to enforce config version integrity.
- Unique `run_uid` for idempotent run registration and efficient lookups.

## Deterministic reproducibility

- Persist seed per run.
- Persist exact configuration version + content hash.
- Persist intervention sequence and optional snapshots/checkpoints.
- Rebuild deterministic replay context from `ReproducibilityRecord` + step data.

## Backup and storage notes

- Prefer external object storage for large `state_blob`/checkpoint payloads in production.
- Use PostgreSQL PITR/WAL archival for recovery guarantees.
- Partition large time-series tables by date or experiment family for long-running deployments.
- Retain snapshot cadence policy (e.g., every N steps + terminal step) to control storage growth.
