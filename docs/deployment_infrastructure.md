# Deployment & Infrastructure Blueprint

## Components
- API service (FastAPI/uvicorn)
- Worker service (distributed batch simulation entrypoint)
- Dashboard service (React static app)
- PostgreSQL persistence
- Prometheus/Grafana observability

## Docker Architecture
- `deploy/docker/Dockerfile.api`: shared API/worker runtime image.
- `deploy/docker/Dockerfile.dashboard`: multi-stage frontend build.
- `deploy/docker/docker-compose.yml`: local multi-service orchestration.

## Kubernetes-Ready Architecture
- Base manifests under `deploy/k8s/base` with Deployments, Service, HPA, ConfigMap.
- Environment-specific overlays under `deploy/k8s/overlays/{dev,prod}`.
- Horizontal scaling is done with HPA and stateless service pods.

## CI/CD Workflows
- `ci.yml` runs Python + frontend test/build.
- `cd.yml` builds/pushes container images to GHCR and deploys prod overlay.

## Security Hardening
- Non-root containers.
- Dropped Linux capabilities and no privilege escalation.
- Example secret manifest separated from ConfigMap.
- Immutable deployment history via container image tags.

## Rollback Strategy
- Keep `revisionHistoryLimit` in deployments.
- Roll back with `kubectl rollout undo deployment/synapses-api -n synapses`.
- Re-deploy prior tagged image via CI/CD manual dispatch.

## Disaster Recovery Considerations
- Back up PostgreSQL volumes and snapshot object storage for experiment artifacts.
- Restore by redeploying manifests and rehydrating DB backups.
- Keep reproducibility metadata (seeds/config hashes) persisted for replay.

## Load Testing
- `scripts/load_test.py` provides a repeatable request generator for smoke-scale load checks.
- Use in CI nightly or pre-release:
  - `python scripts/load_test.py --url http://localhost:8000/health --concurrency 50 --requests-per-worker 200`
