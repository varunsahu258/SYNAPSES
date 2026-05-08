"""Unit tests for the deterministic SimulationEngine."""

import unittest

from synapses import Agent, AgentSignalConfig, Environment, SimulationEngine


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


    def test_custom_signal_config_changes_agent_decisions(self) -> None:
        engine = SimulationEngine(
            agents=[Agent(wealth=95, health=90, satisfaction=90)],
            environment=Environment(food_supply=120, price=10, crime_rate=10),
            signal_config=AgentSignalConfig(risk_scale=8.0),
        )

        history = engine.run(1)

        self.assertEqual(
            history[0]["actions"],
            [{"action": "rest", "reason": "protect_health"}],
        )

    def test_signal_config_clamps_negative_derived_values(self) -> None:
        engine = SimulationEngine(
            agents=[],
            environment=Environment(food_supply=5, price=10, crime_rate=80),
            signal_config=AgentSignalConfig(
                risk_scale=1.0,
                opportunity_price_weight=2.5,
                social_baseline=20,
            ),
        )

        derived = engine._agent_environment_state()

        self.assertEqual(derived["opportunity"], 0)
        self.assertEqual(derived["social"], 0)

    def test_negative_steps_are_rejected(self) -> None:
        engine = SimulationEngine()

        with self.assertRaisesRegex(ValueError, "zero or greater"):
            engine.run(-1)


if __name__ == "__main__":
    unittest.main()
