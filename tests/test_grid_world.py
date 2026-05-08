"""Unit tests for spatial GridWorld implementation."""

import unittest

from synapses.core.spatial import GridWorld


class GridWorldTests(unittest.TestCase):
    def test_init_rejects_invalid_dimensions(self) -> None:
        with self.assertRaisesRegex(ValueError, "width"):
            GridWorld(width=0, height=10)
        with self.assertRaisesRegex(ValueError, "height"):
            GridWorld(width=10, height=0)
        with self.assertRaisesRegex(ValueError, "cell_size"):
            GridWorld(width=10, height=10, cell_size=0)

    def test_coordinate_validation_and_world_to_cell(self) -> None:
        world = GridWorld(width=20, height=10, cell_size=2.0)

        self.assertTrue(world.is_valid_cell((0, 0)))
        self.assertTrue(world.is_valid_cell((19, 9)))
        self.assertFalse(world.is_valid_cell((20, 9)))
        self.assertEqual(world.world_to_cell(3.9, 4.1), (1, 2))

    def test_cell_resource_and_crime_values(self) -> None:
        world = GridWorld(width=8, height=8)
        world.set_cell_values((2, 3), resource=12.5, crime=2.0)

        cell = world.get_cell_values((2, 3))
        self.assertEqual(cell.resource, 12.5)
        self.assertEqual(cell.crime, 2.0)

    def test_registration_movement_unregistration_and_occupancy(self) -> None:
        world = GridWorld(width=8, height=8)
        world.register_agent("a1", (1, 1))
        world.register_agent("a2", (1, 1))

        self.assertEqual(world.agent_count, 2)
        self.assertEqual(world.get_occupants((1, 1)), frozenset({"a1", "a2"}))

        world.move_agent("a2", (2, 1))
        self.assertEqual(world.get_agent_cell("a2"), (2, 1))
        self.assertEqual(world.get_occupants((1, 1)), frozenset({"a1"}))
        self.assertEqual(world.get_occupants((2, 1)), frozenset({"a2"}))

        removed = world.unregister_agent("a1")
        self.assertTrue(removed)
        self.assertEqual(world.agent_count, 1)

    def test_neighbor_and_nearby_queries(self) -> None:
        world = GridWorld(width=5, height=5)
        neighbors = world.neighbors((0, 0), radius=1)
        self.assertEqual(set(neighbors), {(0, 1), (1, 0), (1, 1)})

        nearby = list(world.query_nearby_cells((2, 2), radius=1))
        self.assertEqual(len(nearby), 9)
        self.assertTrue(all(world.is_valid_cell(coord) for coord, _ in nearby))

    def test_bulk_registration_supports_large_counts(self) -> None:
        world = GridWorld(width=50, height=50)
        placements = [(f"agent-{i}", (i % 50, (i // 50) % 50)) for i in range(1200)]

        world.register_agents_bulk(placements)

        self.assertEqual(world.agent_count, 1200)


if __name__ == "__main__":
    unittest.main()
