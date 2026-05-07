import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000';

const client = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Run a SYNAPSES simulation through the FastAPI backend.
 * @param {{numAgents: number, steps: number, taxRate: number}} config
 * @returns {Promise<object>} full JSON response from /run_simulation
 */
export async function runSimulation({ numAgents, steps, taxRate }) {
  const response = await client.post('/run_simulation', {
    num_agents: numAgents,
    steps,
    tax_rate: taxRate,
  });

  return response.data;
}
