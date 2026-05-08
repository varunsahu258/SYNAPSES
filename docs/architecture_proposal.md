# SYNAPSES Architecture Refactor Proposal (Analysis Only)

## Current Architecture Snapshot

The current codebase provides strong deterministic primitives but several concerns are still colocated:

- `synapses/integration.py` combines simulation stepping, causal updates, metrics assembly, and director invocation.
- `synapses/api.py` performs transport concerns and simulation assembly logic.
- `synapses/experiments.py` owns both experiment orchestration and scenario/bootstrap logic.
- Frontend communication currently lives directly in `control-panel/src/api.js` with endpoint-level coupling.

This works for a compact prototype, but scaling research workflows (counterfactuals, alternate policies, batched experiments, reproducibility) will benefit from clearer architectural boundaries.

---

## Proposed Folder Structure

```text
synapses/
  __init__.py

  core/                                # simulation core (domain model + engine)
    __init__.py
    entities/
      __init__.py
      agent.py                         # agent state + deterministic action policy interface
      environment.py                   # environment state + transition rules
    engine/
      __init__.py
      simulation_engine.py             # low-level step executor
      integrated_simulation.py         # orchestrates core loop + hooks
      state_translation.py             # env->agent signal derivation strategies
    causal/
      __init__.py
      structural_models.py             # price/crime causal equations
      counterfactual.py                # counterfactual scenario utilities
    metrics/
      __init__.py
      inequality.py
      wellbeing.py
      safety.py

  ai/                                  # AI systems (separate from domain core)
    __init__.py
    director/
      __init__.py
      policy.py                        # DirectorAI policy + intervention typing
      constraints.py                   # ethical constraints and guardrails
      reward_model.py                  # RL/reward shaping abstractions
    inference/
      __init__.py
      estimators.py                    # causal-inference helper adapters

  experiments/                         # experiment framework
    __init__.py
    scenarios.py                       # reproducible initial-state builders
    variants.py                        # director/no-director/random strategies
    runner.py                          # batch execution + comparison aggregator
    registry.py                        # named experiment definitions

  application/                         # use-case orchestration layer
    __init__.py
    services/
      __init__.py
      simulation_service.py            # app-facing run/stream simulation use-cases
      experiment_service.py            # app-facing experiment use-cases
    dto/
      __init__.py
      requests.py
      responses.py

  interfaces/                          # external I/O adapters
    __init__.py
    api/
      __init__.py
      fastapi_app.py                   # app factory + router registration
      routers/
        __init__.py
        simulation.py
        experiments.py
      websocket/
        __init__.py
        simulation_stream.py
    frontend/
      __init__.py
      contracts.py                     # shared API contract constants/types

control-panel/
  src/
    api/
      client.js                        # axios/http client setup
      simulationApi.js                 # simulation endpoint calls only
      experimentApi.js                 # experiment endpoint calls only
      mappers.js                       # backend DTO -> UI view-model mapping

tests/
  unit/
    core/
    ai/
    experiments/
    application/
    interfaces/
  integration/
    api/
    end_to_end/
```

---

## Dependency Flow Diagram

```text
[Frontend UI]
    |
    v
[Frontend Communication Adapters]
    |
    v
[Interfaces/API Layer (FastAPI routers/websocket)]
    |
    v
[Application Services (use-case orchestration)]
    |                  \
    |                   \--> [AI Systems (Director, constraints, RL adapters)]
    v
[Simulation Core Engine + Domain Entities]
    |
    +--> [Core Causal Models]
    +--> [Core Metrics]

[Experiment Framework]
    |
    +--> depends on [Application Services] for standardized execution
    +--> depends on [Simulation Core] for scenario initialization primitives
```

Dependency rule (strict):
- Outer layers can depend inward.
- Core must not import API, frontend, or experiment runner modules.
- AI modules may depend on core types, but core cannot depend on concrete AI strategies.

---

## Module Responsibilities

### 1) Simulation Core
- **Purpose:** Deterministic, testable simulation semantics.
- **Contains:** Agent/environment state, transition functions, step engine, causal formulas, metric calculations.
- **Must not contain:** FastAPI/Pydantic transport concerns, frontend DTO concerns.
- **Key interface:** `SimulationEngine` + typed state snapshots and hook points.

### 2) AI Systems
- **Purpose:** Decision policies that consume metrics/state and emit interventions.
- **Contains:** Director policy, ethical constraints, RL policy abstractions, inference adapters.
- **Must not contain:** HTTP request parsing, direct websocket mechanics.
- **Key interface:** `recommend(metrics) -> list[Intervention]` and policy configuration protocols.

### 3) API Layer
- **Purpose:** Transport adapter only.
- **Contains:** Routing, validation, serialization, websocket event envelopes, CORS/app factory.
- **Must not contain:** business simulation setup logic beyond invoking services.
- **Key interface:** request DTO -> service call -> response DTO.

### 4) Frontend Communication
- **Purpose:** Encapsulate backend contract and mapping into UI-ready models.
- **Contains:** API client creation, endpoint wrappers, response mappers, retry/timeouts.
- **Must not contain:** simulation logic or experiment semantics.
- **Key interface:** typed functions used by React components.

### 5) Experiment Framework
- **Purpose:** Reproducible scientific workflows and scenario sweeps.
- **Contains:** scenario generation, variant registry, batch runners, comparison summaries.
- **Must not contain:** raw web transport or rendering logic.
- **Key interface:** `run_experiment(spec) -> ExperimentReport`.

---

## Why This Refactor Scales for Research

- Enables **counterfactual testing** by swapping scenario builders and causal modules without touching API or UI.
- Enables **policy benchmarking** by plugging multiple director strategies under a stable AI interface.
- Improves **reproducibility** with explicit experiment registry and deterministic seeds.
- Reduces coupling between **transport** and **domain** logic, improving test speed and confidence.
- Allows incremental migration: files can be moved behind compatibility shims while preserving current imports.

---

## Incremental Migration Strategy (No Implementation in This Step)

1. Introduce package skeletons and re-export existing modules.
2. Move pure core modules first (`agent`, `environment`, `causal`, `metrics`).
3. Introduce `application/services` and redirect `api.py` endpoints through services.
4. Split `experiments.py` into `scenarios`, `variants`, and `runner`.
5. Split frontend API file into client + endpoint modules + mappers.
6. Add import deprecation shims and remove only after test parity.

