export default function GridCanvas({ gridState }) {
  if (!gridState) {
    return (
      <article className="dashboard-card">
        <h2 className="text-xl font-black text-slate-950">Spatial grid</h2>
        <p className="mt-2 text-sm font-semibold text-slate-500">Run a simulation to render the grid.</p>
      </article>
    );
  }

  const { width, height, agents = [] } = gridState;
  const cellSize = Math.max(16, Math.floor(260 / Math.max(width, height, 1)));
  const agentMap = new Map(agents.map((a) => [a.position.join(','), a]));

  return (
    <article className="dashboard-card min-w-0">
      <h2 className="text-xl font-black text-slate-950">Spatial grid</h2>
      <div className="mt-4 overflow-auto">
        <div
          className="grid gap-1 rounded-xl bg-slate-100 p-2"
          style={{ gridTemplateColumns: `repeat(${width}, minmax(0, 1fr))` }}
        >
          {Array.from({ length: width * height }, (_, index) => {
            const x = index % width;
            const y = Math.floor(index / width);
            const key = `${x},${y}`;
            const agent = agentMap.get(key);
            return (
              <div
                className={`flex items-center justify-center rounded ${agent ? 'bg-emerald-500 text-white' : 'bg-white text-slate-300'}`}
                key={key}
                style={{ width: cellSize, height: cellSize }}
                title={agent ? `Agent ${agent.agent_id} @ (${x}, ${y})` : `(${x}, ${y})`}
              >
                {agent ? '●' : ''}
              </div>
            );
          })}
        </div>
      </div>
    </article>
  );
}
