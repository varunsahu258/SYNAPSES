"""Unit tests for the integrated SYNAPSES simulation runner."""

import unittest

from synapses import Agent, DirectorAI, Environment, IntegratedSimulation, run_full_simulation


class IntegratedSimulationTests(unittest.TestCase):
    """Verify all core modules work together in a full simulation."""

    def test_full_simulation_returns_metrics_over_time(self) -> None:
        simulation = IntegratedSimulation(
            agents=[
                Agent(wealth=0, health=80, satisfaction=30),
                Agent(wealth=100, health=80, satisfaction=70),
            ],
            environment=Environment(food_supply=49, price=10, crime_rate=10),
            director=DirectorAI(),
        )

        metrics_over_time = simulation.run(10)

        self.assertEqual(len(metrics_over_time), 10)
        self.assertEqual(metrics_over_time[0]["step"], 1)
        self.assertEqual(metrics_over_time[-1]["step"], 10)
        self.assertEqual(
            metrics_over_time[-1]["crime_history"],
            [50, 49, 48, 47, 46, 45, 44, 43, 42, 41],
        )
        self.assertEqual(metrics_over_time[-1]["average_satisfaction"], 50.0)
        self.assertAlmostEqual(metrics_over_time[-1]["gini"], 0.5)
        self.assertIn(
            {"action": "redistribute_resources", "reason": "high_inequality"},
            metrics_over_time[-1]["interventions"],
        )

    def test_iter_steps_yields_metrics_as_each_step_completes(self) -> None:
        simulation = IntegratedSimulation(
            agents=[Agent(wealth=50, health=80, satisfaction=80)],
            environment=Environment(food_supply=100, price=10, crime_rate=10),
            director=DirectorAI(),
        )

        step_iterator = simulation.iter_steps(2)
        first = next(step_iterator)
        second = next(step_iterator)

        self.assertEqual(first["step"], 1)
        self.assertEqual(second["step"], 2)
        self.assertEqual(len(simulation.history), 2)


    def test_agents_receive_isolated_environment_snapshots(self) -> None:
        class MutatingAgent:
            wealth = 50
            health = 80
            satisfaction = 80

            def act(self, state: dict[str, int]) -> dict[str, str]:
                state["risk"] = 999
                return {"action": "maintain", "reason": "test"}

        class ObservingAgent:
            wealth = 50
            health = 80
            satisfaction = 80

            def __init__(self) -> None:
                self.observed_risk: int | None = None

            def act(self, state: dict[str, int]) -> dict[str, str]:
                self.observed_risk = state["risk"]
                return {"action": "maintain", "reason": "test"}

        observer = ObservingAgent()
        simulation = IntegratedSimulation(
            agents=[MutatingAgent(), observer],
            environment=Environment(food_supply=100, price=10, crime_rate=10),
        )

        simulation.run(1)

        self.assertEqual(observer.observed_risk, 10)

    def test_history_records_agent_actions_and_environment_state(self) -> None:
        simulation = IntegratedSimulation(
            agents=[Agent(wealth=10, health=80, satisfaction=80)],
            environment=Environment(food_supply=100, price=10, crime_rate=10),
        )

        simulation.run(1)

        self.assertEqual(
            simulation.history,
            (
                {
                    "step": 1,
                    "actions": [{"action": "work", "reason": "increase_wealth"}],
                    "environment": {"food_supply": 105, "price": 10, "crime_rate": 0},
                },
            ),
        )

    def test_convenience_function_runs_full_simulation(self) -> None:
        metrics_over_time = run_full_simulation(
            steps=2,
            agents=[Agent(wealth=50, health=80, satisfaction=80)],
            environment=Environment(food_supply=100, price=10, crime_rate=10),
        )

        self.assertEqual(len(metrics_over_time), 2)
        self.assertEqual(metrics_over_time[-1]["crime_history"], [0, 0])
        self.assertEqual(
            metrics_over_time[-1]["interventions"],
            [{"action": "monitor", "reason": "stable_metrics"}],
        )

    def test_negative_steps_are_rejected(self) -> None:
        simulation = IntegratedSimulation()

        with self.assertRaisesRegex(ValueError, "zero or greater"):
            simulation.run(-1)


if __name__ == "__main__":
    unittest.main()
