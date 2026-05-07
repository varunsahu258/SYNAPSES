"""Unit tests for SYNAPSES metrics functions."""

import unittest

from synapses import Agent, average_satisfaction, gini_coefficient, track_crime


class MetricsTests(unittest.TestCase):
    """Verify metric calculations are deterministic and independent."""

    def test_gini_coefficient_for_equal_values_is_zero(self) -> None:
        self.assertEqual(gini_coefficient([10, 10, 10]), 0.0)

    def test_gini_coefficient_for_unequal_values(self) -> None:
        self.assertAlmostEqual(gini_coefficient([0, 0, 100]), 2 / 3)

    def test_gini_coefficient_handles_empty_and_zero_values(self) -> None:
        self.assertEqual(gini_coefficient([]), 0.0)
        self.assertEqual(gini_coefficient([0, 0, 0]), 0.0)

    def test_gini_coefficient_rejects_negative_values(self) -> None:
        with self.assertRaisesRegex(ValueError, "non-negative"):
            gini_coefficient([10, -1, 20])

    def test_average_satisfaction_returns_mean(self) -> None:
        agents = [
            Agent(wealth=10, health=80, satisfaction=20),
            Agent(wealth=20, health=80, satisfaction=80),
        ]

        self.assertEqual(average_satisfaction(agents), 50.0)

    def test_average_satisfaction_returns_zero_for_no_agents(self) -> None:
        self.assertEqual(average_satisfaction([]), 0.0)

    def test_track_crime_extracts_crime_rates_in_order(self) -> None:
        history = [
            {"step": 1, "environment": {"crime_rate": 10}},
            {"step": 2, "environment": {"crime_rate": 8}},
            {"step": 3, "environment": {"crime_rate": 6}},
        ]

        self.assertEqual(track_crime(history), [10, 8, 6])

    def test_track_crime_treats_missing_values_as_zero(self) -> None:
        history = [
            {"step": 1, "environment": {}},
            {"step": 2},
            {"step": 3, "environment": {"crime_rate": "high"}},
        ]

        self.assertEqual(track_crime(history), [0, 0, 0])


if __name__ == "__main__":
    unittest.main()
