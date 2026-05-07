import { useState } from 'react';

import { runSimulation } from './api';
import MetricsChart from './components/MetricsChart';
import './App.css';

const DEFAULT_FORM = {
  numAgents: 3,
  steps: 10,
  taxRate: 0.25,
};

/**
 * SYNAPSES frontend control panel for running one simulation and viewing JSON.
 */
function App() {
  const [form, setForm] = useState(DEFAULT_FORM);
  const [result, setResult] = useState(null);
  const [status, setStatus] = useState('Ready');
  const [isRunning, setIsRunning] = useState(false);

  function updateField(field, value) {
    setForm((current) => ({
      ...current,
      [field]: Number(value),
    }));
  }

  async function handleRunSimulation(event) {
    event.preventDefault();
    setIsRunning(true);
    setStatus('Running simulation...');

    try {
      const nextResult = await runSimulation(form);
      setResult(nextResult);
      setStatus('Simulation complete');
    } catch (error) {
      setStatus(`Simulation failed: ${error.message}`);
    } finally {
      setIsRunning(false);
    }
  }

  const metrics = result?.metrics_over_time ?? [];

  return (
    <main className="app-shell">
      <section className="hero-card">
        <p className="eyebrow">SYNAPSES</p>
        <h1>Simulation Control Panel</h1>
        <p>
          Run a simulation through the FastAPI backend and inspect the raw JSON result.
        </p>
      </section>

      <form className="control-card" onSubmit={handleRunSimulation}>
        <div className="field-grid">
          <label>
            Agents
            <input
              min="1"
              type="number"
              value={form.numAgents}
              onChange={(event) => updateField('numAgents', event.target.value)}
            />
          </label>
          <label>
            Steps
            <input
              min="0"
              type="number"
              value={form.steps}
              onChange={(event) => updateField('steps', event.target.value)}
            />
          </label>
          <label>
            Tax rate
            <input
              max="1"
              min="0"
              step="0.01"
              type="number"
              value={form.taxRate}
              onChange={(event) => updateField('taxRate', event.target.value)}
            />
          </label>
        </div>

        <button disabled={isRunning} type="submit">
          {isRunning ? 'Running...' : 'Run Simulation'}
        </button>
      </form>

      <p className="status" role="status">
        {status}
      </p>

      <section className="result-grid">
        <MetricsChart metrics={metrics} />

        <article className="json-card">
          <div className="card-header">
            <h2>JSON result</h2>
            <span>{metrics.length} steps</span>
          </div>
          <pre>{result ? JSON.stringify(result, null, 2) : 'No simulation result yet.'}</pre>
        </article>
      </section>
    </main>
  );
}

export default App;
