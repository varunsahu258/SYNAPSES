"""Tests for counterfactual branching engine."""

from __future__ import annotations

from synapses.agent import Agent
from synapses.environment import Environment
from synapses.experiments import CounterfactualEngine


def _boost_food(environment: Environment, agents: list[Agent], _rng) -> None:
    environment.food_supply += 10


def _crime_spike(environment: Environment, agents: list[Agent], _rng) -> None:
    environment.crime_rate += 10


def test_branches_do_not_mutate_base_state() -> None:
    agents = [Agent(wealth=20, health=70, satisfaction=50), Agent(wealth=40, health=60, satisfaction=45)]
    environment = Environment(food_supply=100, price=10, crime_rate=10)
    engine = CounterfactualEngine(base_agents=agents, base_environment=environment, seed=123)

    baseline = engine.create_branch("baseline")
    policy = engine.create_branch("policy", interventions={1: [_boost_food]})
    baseline.run(steps=2)
    policy.run(steps=2)

    assert environment.food_supply == 100
    assert [a.wealth for a in agents] == [20, 40]


def test_compare_reports_branch_metrics_and_deltas() -> None:
    engine = CounterfactualEngine(
        base_agents=[Agent(), Agent(wealth=30)],
        base_environment=Environment(),
        seed=7,
    )
    engine.create_branch("baseline")
    engine.create_branch("intervened", interventions={1: [_boost_food], 2: [_crime_spike]})
    engine.run_all(steps=3)

    report = engine.compare("baseline")

    assert report["baseline"] == "baseline"
    assert "branch_comparison" in report
    assert "intervened" in report["branch_comparison"]
    assert "delta_vs_baseline" in report["branch_comparison"]["intervened"]


def test_replay_is_deterministic() -> None:
    engine = CounterfactualEngine(
        base_agents=[Agent(wealth=10), Agent(wealth=50)],
        base_environment=Environment(food_supply=90, price=12, crime_rate=15),
        seed=11,
    )
    engine.create_branch("policy", interventions={1: [_boost_food]})
    first = engine.run_all(steps=4)["policy"]
    replay = engine.replay_branch("policy")

    assert first == replay


def test_snapshot_index_available_for_storage() -> None:
    engine = CounterfactualEngine(base_agents=[Agent()], base_environment=Environment())
    branch = engine.create_branch("baseline")
    branch.run(steps=2)

    index = engine.storage_snapshot_index()
    assert index["baseline"] == [0, 1, 2]
