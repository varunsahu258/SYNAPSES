"""Unit tests for the deterministic Agent module."""

import unittest

from synapses import Agent


class AgentTests(unittest.TestCase):
    """Verify Agent.act returns deterministic action dictionaries."""

    def test_low_health_prioritizes_rest(self) -> None:
        agent = Agent(wealth=80, health=20, satisfaction=80)

        self.assertEqual(
            agent.act({"risk": 0, "opportunity": 100, "social": 100}),
            {"action": "rest", "reason": "protect_health"},
        )

    def test_high_risk_prioritizes_rest(self) -> None:
        agent = Agent(wealth=80, health=80, satisfaction=80)

        self.assertEqual(
            agent.act({"risk": 70}),
            {"action": "rest", "reason": "protect_health"},
        )

    def test_low_wealth_with_opportunity_chooses_work(self) -> None:
        agent = Agent(wealth=10, health=80, satisfaction=80)

        self.assertEqual(
            agent.act({"risk": 20, "opportunity": 50}),
            {"action": "work", "reason": "increase_wealth"},
        )

    def test_low_satisfaction_chooses_socialize(self) -> None:
        agent = Agent(wealth=80, health=80, satisfaction=10)

        self.assertEqual(
            agent.act({"risk": 0, "opportunity": 0}),
            {"action": "socialize", "reason": "increase_satisfaction"},
        )

    def test_balanced_state_chooses_maintain(self) -> None:
        agent = Agent(wealth=80, health=80, satisfaction=80)

        self.assertEqual(
            agent.act(None),
            {"action": "maintain", "reason": "balanced_state"},
        )

    def test_non_numeric_environment_values_are_neutral(self) -> None:
        agent = Agent(wealth=80, health=80, satisfaction=80)

        self.assertEqual(
            agent.act({"risk": "high", "opportunity": "many", "social": "yes"}),
            {"action": "maintain", "reason": "balanced_state"},
        )


if __name__ == "__main__":
    unittest.main()
