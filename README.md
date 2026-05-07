# SYNAPSES

SYNAPSES contains small, dependency-free workflow utilities in Python and
JavaScript. The current baseline models the required engineering cadence:

1. Plan
2. Code
3. Test

## Python

```bash
python -m unittest discover -s tests
```

## JavaScript

```bash
npm test
```

Each implementation is intentionally modular, independently testable, and kept
free of external runtime dependencies.

## Agent

```python
from synapses import Agent

agent = Agent(wealth=30, health=80, satisfaction=70)
action = agent.act({"risk": 10, "opportunity": 80})
# {"action": "work", "reason": "increase_wealth"}
```

The agent is deterministic and returns an action dictionary from the supplied
environment state.

## Environment

```python
from synapses import Environment

environment = Environment(food_supply=100, price=10, crime_rate=10)
state = environment.update([{"action": "work"}])
# {"food_supply": 105, "price": 10, "crime_rate": 9}
```

The environment applies deterministic updates to `food_supply`, `price`, and
`crime_rate` from action dictionaries.

## Simulation Engine

```python
from synapses import Agent, Environment, SimulationEngine

engine = SimulationEngine(
    agents=[Agent(wealth=80, health=80, satisfaction=80)],
    environment=Environment(food_supply=100, price=10, crime_rate=10),
)
history = engine.run(10)
```

The simulation engine manages agents, calls each agent for an action on every
step, updates the environment, and returns state history.

## Causal Model

```python
from synapses import crime_from_price_and_inequality, price_from_food_supply

price = price_from_food_supply(food_supply=49)
crime = crime_from_price_and_inequality(price=price, inequality=30)
```

The causal model functions are deterministic and independently testable:
`price = f(food_supply)` and `crime = f(price, inequality)`.

## Metrics

```python
from synapses import average_satisfaction, gini_coefficient, track_crime

wealth_gini = gini_coefficient([10, 20, 70])
mean_satisfaction = average_satisfaction(agents)
crime_series = track_crime(history)
```

Metrics are stateless helpers for inequality, satisfaction, and crime tracking.

## Director AI

```python
from synapses import DirectorAI

director = DirectorAI()
interventions = director.recommend({
    "gini": 0.5,
    "average_satisfaction": 35,
    "crime_rate": 60,
})
```

The director uses simple rule-based logic to convert global metrics into
intervention action dictionaries.

## Full Integration

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

The integrated runner coordinates agents, environment updates, causal crime,
metrics, and Director AI interventions, then returns metrics over time.

## FastAPI App

Run the API locally:

```bash
uvicorn synapses.api:app --reload
```

Example request:

```bash
curl -X POST http://127.0.0.1:8000/run_simulation \
  -H "Content-Type: application/json" \
  -d '{"num_agents": 3, "steps": 10, "tax_rate": 0.25}'
```

The endpoint returns `metrics_over_time` from the integrated simulation stack.

Run comparison experiments:

```bash
curl -X POST http://127.0.0.1:8000/run_experiment \
  -H "Content-Type: application/json" \
  -d '{"num_agents": 3, "steps": 10, "tax_rate": 0.25}'
```

The experiment endpoint runs `no_director`, `random`, and `director_based`
variants from the same starting conditions and returns comparison results.

