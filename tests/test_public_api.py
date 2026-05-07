"""Regression tests for the public SYNAPSES package exports."""

import unittest

import synapses
from synapses.experiments import build_agents, run_experiment


class PublicAPITests(unittest.TestCase):
    """Verify convenience exports remain available from ``synapses``."""

    def test_experiment_helpers_are_exported_from_package_root(self) -> None:
        self.assertIs(synapses.build_agents, build_agents)
        self.assertIs(synapses.run_experiment, run_experiment)
        self.assertIn("build_agents", synapses.__all__)
        self.assertIn("run_experiment", synapses.__all__)


if __name__ == "__main__":
    unittest.main()
