# Spatial Grid System Design and Usage

## Example Usage

```python
from synapses.core.spatial import GridWorld

world = GridWorld(width=200, height=200, cell_size=5.0)

world.set_cell_values((10, 12), resource=35.0, crime=4.0)
world.register_agent("agent-001", (10, 12))

neighbors = world.neighbors((10, 12), radius=1)
local_cells = list(world.query_nearby_cells((10, 12), radius=2))

world.move_agent("agent-001", (11, 12))
world.unregister_agent("agent-001")
```

## Complexity Analysis

- `is_valid_cell`: **O(1)**.
- `world_to_cell`: **O(1)**.
- `set_cell_values` / `get_cell_values`: **O(1)** average (hash-map access).
- `register_agent` / `unregister_agent` / `move_agent`: **O(1)** average with dual indexes.
- `get_occupants`: **O(k)** to materialize immutable snapshot where *k* is occupants in a single cell.
- `neighbors` / `query_nearby_cells`: **O(r^2)** over bounded local window with radius *r*.
- `register_agents_bulk`: **O(n)** for *n* agent placements.

This supports 1000+ agents efficiently because hot operations remain constant-time on average and neighborhood work scales with local query radius, not global world size.

## Future Extensibility Notes

- **Chunk streaming**: add a chunk index keyed by `(chunk_x, chunk_y)` and swap sparse cell dict storage to per-chunk maps.
- **Pathfinding**: expose movement-cost and traversability overlays per cell and plug A*/D* search modules without changing occupancy APIs.
- **Rendering**: keep rendering adapters outside this module and consume immutable snapshots (`get_occupants`, `query_nearby_cells`) via interface layer.
- **Metrics**: build spatial aggregators (heatmaps, per-neighborhood crime/resource stats) on top of this core without coupling to simulation execution policy.
