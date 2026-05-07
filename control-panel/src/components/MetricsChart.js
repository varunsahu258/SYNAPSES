import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

/**
 * Render simulation metrics over time using Recharts.
 * @param {{metrics: Array<object>}} props
 */
export default function MetricsChart({ metrics }) {
  if (!metrics.length) {
    return <p className="empty-state">Run a simulation to see metrics over time.</p>;
  }

  return (
    <div className="chart-card">
      <h2>Metrics over time</h2>
      <ResponsiveContainer width="100%" height={320}>
        <LineChart data={metrics} margin={{ top: 10, right: 20, bottom: 10, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="step" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="gini" stroke="#2563eb" strokeWidth={2} />
          <Line
            type="monotone"
            dataKey="average_satisfaction"
            stroke="#16a34a"
            strokeWidth={2}
          />
          <Line type="monotone" dataKey="crime_rate" stroke="#dc2626" strokeWidth={2} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
