"""Unit tests for the rule-based DirectorAI."""

import unittest

from synapses import DirectorAI


class DirectorAITests(unittest.TestCase):
    """Verify director interventions are simple and deterministic."""

    def test_high_gini_triggers_redistribution(self) -> None:
        director = DirectorAI()

        self.assertEqual(
            director.recommend({"gini": 0.5, "average_satisfaction": 80, "crime_rate": 10}),
            [{"action": "redistribute_resources", "reason": "high_inequality"}],
        )

    def test_low_satisfaction_triggers_public_services(self) -> None:
        director = DirectorAI()

        self.assertEqual(
            director.recommend({"gini": 0.1, "average_satisfaction": 30, "crime_rate": 10}),
            [{"action": "fund_public_services", "reason": "low_satisfaction"}],
        )

    def test_high_crime_triggers_safety_programs(self) -> None:
        director = DirectorAI()

        self.assertEqual(
            director.recommend({"gini": 0.1, "average_satisfaction": 80, "crime_rate": 60}),
            [{"action": "increase_safety_programs", "reason": "high_crime"}],
        )

    def test_multiple_rules_return_ordered_interventions(self) -> None:
        director = DirectorAI()

        self.assertEqual(
            director.recommend({"gini": 0.8, "average_satisfaction": 20, "crime_rate": 90}),
            [
                {"action": "redistribute_resources", "reason": "high_inequality"},
                {"action": "fund_public_services", "reason": "low_satisfaction"},
                {"action": "increase_safety_programs", "reason": "high_crime"},
            ],
        )

    def test_stable_metrics_return_monitor_action(self) -> None:
        director = DirectorAI()

        self.assertEqual(
            director.recommend({"gini": 0.2, "average_satisfaction": 70, "crime_rate": 20}),
            [{"action": "monitor", "reason": "stable_metrics"}],
        )

    def test_missing_metrics_are_treated_as_stable(self) -> None:
        director = DirectorAI()

        self.assertEqual(
            director.recommend(None),
            [{"action": "monitor", "reason": "stable_metrics"}],
        )

    def test_custom_thresholds_are_supported(self) -> None:
        director = DirectorAI(gini_threshold=0.2, satisfaction_threshold=90, crime_threshold=20)

        self.assertEqual(
            director.recommend({"gini": 0.3, "average_satisfaction": 80, "crime_rate": 21}),
            [
                {"action": "redistribute_resources", "reason": "high_inequality"},
                {"action": "fund_public_services", "reason": "low_satisfaction"},
                {"action": "increase_safety_programs", "reason": "high_crime"},
            ],
        )


if __name__ == "__main__":
    unittest.main()
