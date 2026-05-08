# SYNAPSES

SYNAPSES is a research-grade socio-economic simulation platform built around modular, deterministic components for simulation, AI governance, experimentation, explainability, and reproducibility.

## Project Features

- **Simulation Core**
  - Deterministic agents, environment dynamics, simulation engine, and causal utilities.
  - Configurable signal derivation and metrics tracking.
- **Spatial Simulation**
  - 2D `GridWorld` with localized resources/crime, occupancy tracking, neighborhood queries, and efficient agent registration/movement primitives.
- **AI Systems**
  - Rule-based `DirectorAI`.
  - Reinforcement-learning Director stack (Gym-compatible wrapper + PPO pipeline hooks).
- **Experiment Framework**
  - Scenario experiments, counterfactual branching, Monte Carlo/batch orchestration, parameter sweeps, CI summaries, and export tooling.
- **Explainability**
  - Trend-aware, evidence-backed narrative explanations for key socio-economic shifts and interventions.
- **Persistence & Reproducibility**
  - SQLAlchemy persistence models/services for runs, metrics, interventions, snapshots, config versions, and checkpoints.
  - Alembic migration scaffolding for database evolution.
- **API & Realtime Dashboard Integration**
  - FastAPI REST endpoints for simulation/experiments.
  - WebSocket streaming protocol for dashboard metrics/events/spatial snapshots.
- **Deployment & Operations**
  - Dockerized services, Compose stack, Kubernetes manifests (base + overlays), GitHub Actions CI/CD, Prometheus/Grafana observability, and load-testing utility.

---

## Architecture (High Level)

```text
synapses/core           -> simulation/causal/entities/metrics/spatial primitives
synapses/ai             -> director systems (rule-based + RL tools)
synapses/application    -> orchestration services (simulation, experiments, explainability)
synapses/interfaces     -> FastAPI/WebSocket interface adapters
synapses/experiments    -> orchestration, counterfactuals, reporting
synapses/persistence    -> DB config, ORM models, persistence/reproducibility services
```

This separation keeps simulation logic independent from UI/rendering and transport layers.

---

## Steps to Operate and Use the Project

## 1) Local Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- npm 9+

### Install dependencies
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -r requirements.txt  # if present in your environment
```

Frontend dependencies:
```bash
cd control-panel
npm install
cd ..
```

## 2) Run Tests (Validation First)

Backend tests:
```bash
pytest -q
```

Optional quick checks:
```bash
python -m py_compile scripts/load_test.py
```

## 3) Run the FastAPI Backend

```bash
uvicorn synapses.api:app --host 0.0.0.0 --port 8000 --reload
```

Useful endpoints:
- `POST /run_simulation`
- `POST /run_experiment`
- `WS  /ws/dashboard`

Example simulation call:
```bash
curl -X POST http://127.0.0.1:8000/run_simulation \
  -H "Content-Type: application/json" \
  -d '{"num_agents": 5, "steps": 20, "tax_rate": 0.25}'
```

## 4) Run the React Dashboard

```bash
cd control-panel
npm start
```

Open the local URL printed by React (typically `http://localhost:3000`) and connect to backend `http://127.0.0.1:8000`.

## 5) Run with Docker Compose

```bash
docker compose -f deploy/docker/docker-compose.yml up --build
```

Services include API, worker, dashboard, Postgres, Prometheus, and Grafana.

## 6) Kubernetes (Base/Overlay)

```bash
kubectl apply -k deploy/k8s/overlays/dev
# or
kubectl apply -k deploy/k8s/overlays/prod
```

Use `deploy/k8s/base/secret.example.yaml` as a template for real secrets.

## 7) Database Migrations (Persistence)

From your configured environment:
```bash
alembic -c synapses/persistence/alembic.ini upgrade head
```

(Adjust path/config as needed for your deployment layout.)

## 8) Load Testing

```bash
python scripts/load_test.py --help
python scripts/load_test.py --url http://127.0.0.1:8000/run_simulation --concurrency 20 --requests 200
```

## 9) Research/Experiment Workflows

Typical pipeline:
1. Run baseline and variants through experiment orchestration.
2. Export JSON/CSV summaries.
3. Generate markdown publication reports.
4. Optionally branch counterfactual timelines and compare outcome deltas.

---

## Minimal Usage Examples

### Agent + Environment + Simulation

```python
from synapses import Agent, Environment, SimulationEngine

engine = SimulationEngine(
    agents=[Agent(wealth=80, health=80, satisfaction=80)],
    environment=Environment(food_supply=100, price=10, crime_rate=10),
)
history = engine.run(10)
```

### Full Integration Runner

```python
from synapses import Agent, DirectorAI, Environment, run_full_simulation

metrics_over_time = run_full_simulation(
    steps=10,
    agents=[
        Agent(wealth=0, health=80, satisfaction=30),
        Agent(wealth=100, health=80, satisfaction=70),
    ],
    environment=Environment(food_supply=49, price=10, crime_rate=10),
    director=DirectorAI(),
)
```

---

## Additional Documentation

- `docs/architecture_proposal.md`
- `docs/spatial_grid_system.md`
- `docs/persistence_architecture.md`
- `docs/deployment_infrastructure.md`

---

## Notes

- Keep simulation logic decoupled from rendering/UI concerns.
- Prefer deterministic seeds/config snapshots for reproducible research runs.
- Use package-layer APIs (`synapses.*`) rather than reaching into internal modules where possible.
