"""Unit tests for the deterministic SimulationEngine."""

import unittest

from synapses import Agent, Environment, SimulationEngine


class SimulationEngineTests(unittest.TestCase):
    """Verify simulations manage agents, actions, and state history."""

    def test_run_ten_steps_returns_state_history(self) -> None:
        engine = SimulationEngine(
            agents=[Agent(wealth=80, health=80, satisfaction=80)],
            environment=Environment(food_supply=100, price=10, crime_rate=10),
        )

        history = engine.run(10)

        self.assertEqual(len(history), 10)
        self.assertEqual(history[0]["step"], 1)
        self.assertEqual(history[-1]["step"], 10)
        self.assertEqual(
            history[-1]["environment"],
            {"food_supply": 80, "price": 10, "crime_rate": 0},
        )

    def test_each_step_records_agent_actions(self) -> None:
        engine = SimulationEngine(
            agents=[
                Agent(wealth=10, health=80, satisfaction=80),
                Agent(wealth=80, health=80, satisfaction=10),
            ],
            environment=Environment(food_supply=100, price=10, crime_rate=10),
        )

        history = engine.run(1)

        self.assertEqual(
            history,
            [
                {
                    "step": 1,
                    "actions": [
                        {"action": "work", "reason": "increase_wealth"},
                        {"action": "socialize", "reason": "increase_satisfaction"},
                    ],
                    "environment": {"food_supply": 103, "price": 10, "crime_rate": 8},
                }
            ],
        )

    def test_add_agent_registers_agent_for_future_steps(self) -> None:
        engine = SimulationEngine(environment=Environment())
        engine.add_agent(Agent(wealth=80, health=20, satisfaction=80))

        history = engine.run(1)

        self.assertEqual(
            history[0]["actions"],
            [{"action": "rest", "reason": "protect_health"}],
        )

    def test_zero_steps_returns_empty_history(self) -> None:
        engine = SimulationEngine(agents=[Agent()], environment=Environment())

        self.assertEqual(engine.run(0), [])

    def test_negative_steps_are_rejected(self) -> None:
        engine = SimulationEngine()

        with self.assertRaisesRegex(ValueError, "zero or greater"):
            engine.run(-1)


if __name__ == "__main__":
    unittest.main()
