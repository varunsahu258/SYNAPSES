"""Unit tests for experiment comparison orchestration."""

import unittest

from synapses.experiments import build_agents, run_experiment


class ExperimentTests(unittest.TestCase):
    """Verify experiment variants return comparable metrics."""

    def test_run_experiment_returns_all_variants_and_comparison(self) -> None:
        result = run_experiment(num_agents=3, steps=2, tax_rate=0.25)

        self.assertEqual(
            set(result["experiments"]),
            {"no_director", "random", "director_based"},
        )
        self.assertEqual(
            set(result["comparison"]),
            {"no_director", "random", "director_based"},
        )

        for variant in result["experiments"].values():
            self.assertEqual(len(variant["metrics_over_time"]), 2)
            self.assertEqual(variant["final_metrics"]["step"], 2)
            self.assertIn("crime_rate", variant["final_metrics"])

    def test_no_director_has_no_interventions(self) -> None:
        result = run_experiment(num_agents=2, steps=1)

        self.assertEqual(
            result["comparison"]["no_director"]["interventions"],
            [],
        )

    def test_random_director_is_reproducible(self) -> None:
        first = run_experiment(num_agents=2, steps=3)
        second = run_experiment(num_agents=2, steps=3)

        self.assertEqual(
            first["experiments"]["random"]["metrics_over_time"],
            second["experiments"]["random"]["metrics_over_time"],
        )


    def test_director_variants_produce_different_outcomes(self) -> None:
        result = run_experiment(num_agents=2, steps=3)

        no_director = result["comparison"]["no_director"]
        random_director = result["comparison"]["random"]
        director_based = result["comparison"]["director_based"]

        self.assertNotEqual(
            result["experiments"]["random"]["metrics_over_time"][-1]["food_supply"],
            result["experiments"]["no_director"]["metrics_over_time"][-1]["food_supply"],
        )
        self.assertNotEqual(random_director["interventions"], no_director["interventions"])
        self.assertNotEqual(director_based["interventions"], no_director["interventions"])

    def test_build_agents_applies_tax_rate(self) -> None:
        untaxed = build_agents(num_agents=3, tax_rate=0.0)
        taxed = build_agents(num_agents=3, tax_rate=1.0)

        self.assertEqual([agent.wealth for agent in untaxed], [20, 30, 40])
        self.assertEqual([agent.wealth for agent in taxed], [30, 30, 30])

    def test_invalid_experiment_input_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "num_agents"):
            run_experiment(num_agents=0, steps=1)

        with self.assertRaisesRegex(ValueError, "steps"):
            run_experiment(num_agents=1, steps=-1)

        with self.assertRaisesRegex(ValueError, "tax_rate"):
            run_experiment(num_agents=1, steps=1, tax_rate=2.0)


if __name__ == "__main__":
    unittest.main()
