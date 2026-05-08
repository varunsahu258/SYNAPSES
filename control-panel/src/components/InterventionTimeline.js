export default function InterventionTimeline({ timeline }) {
  if (!timeline?.length) {
    return (
      <article className="dashboard-card">
        <h2 className="text-xl font-black text-slate-950">Director interventions</h2>
        <p className="mt-2 text-sm font-semibold text-slate-500">Run an experiment to view intervention decisions.</p>
      </article>
    );
  }

  return (
    <article className="dashboard-card min-w-0">
      <h2 className="text-xl font-black text-slate-950">Director interventions</h2>
      <ul className="mt-4 max-h-72 space-y-3 overflow-auto pr-1">
        {timeline.map((entry) => (
          <li className="rounded-xl border border-slate-200 bg-slate-50 p-3" key={`${entry.step}-${entry.action}`}>
            <p className="text-xs font-black uppercase tracking-wide text-slate-500">Step {entry.step}</p>
            <p className="mt-1 text-sm font-black text-slate-900">{entry.action}</p>
            <p className="text-xs font-semibold text-slate-600">{entry.reason}</p>
          </li>
        ))}
      </ul>
    </article>
  );
}
