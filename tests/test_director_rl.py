from __future__ import annotations
import unittest

from synapses.ai.director.rl import DirectorAction, DirectorGymEnv, DirectorObservation, RewardWeights, compute_reward, evaluate_observation, run_baseline_rollout

class DirectorRLTests(unittest.TestCase):
    def test_action_round_trip_clipping(self) -> None:
        action = DirectorAction.from_array([2, -2, 0.5, 0, -0.5, 0.25])
        arr = action.as_array()
        self.assertTrue(all(-1.0 <= v <= 1.0 for v in arr))

    def test_reward_penalizes_bad_social_conditions(self) -> None:
        good = DirectorObservation(0.2, 0.2, 0.8, 0.8, 0.2, 0.8, 0.2)
        bad = DirectorObservation(0.8, 0.8, 0.2, 0.3, 0.8, 0.2, 0.8)
        self.assertGreater(compute_reward(good, RewardWeights()), compute_reward(bad, RewardWeights()))

    def test_environment_step_shapes_and_metrics(self) -> None:
        try:
            env = DirectorGymEnv(episode_length=5, seed=123)
        except ImportError:
            self.skipTest("gymnasium not installed")
        obs, _ = env.reset(seed=123)
        self.assertEqual(len(obs), 7)
        next_obs, reward, terminated, truncated, info = env.step([0.0] * 6)
        self.assertEqual(len(next_obs), 7)
        self.assertIsInstance(reward, float)
        self.assertFalse(truncated)
        self.assertIn("metrics", info)
        self.assertFalse(terminated)

    def test_baseline_rollout_returns_required_metrics(self) -> None:
        try:
            env = DirectorGymEnv(episode_length=10, seed=1)
        except ImportError:
            self.skipTest("gymnasium not installed")
        metrics = run_baseline_rollout(env, policy="do_nothing", steps=5)
        self.assertSetEqual(set(metrics), {"inequality", "crime", "stability", "survival_rate", "resource_efficiency"})

    def test_evaluate_observation_ranges(self) -> None:
        metrics = evaluate_observation(DirectorObservation(0.4, 0.3, 0.7, 0.8, 0.4, 0.6, 0.2))
        self.assertTrue(all(0.0 <= v <= 1.0 for v in metrics.values()))

if __name__ == '__main__':
    unittest.main()
