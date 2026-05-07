import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

const EXPERIMENT_LINES = [
  {
    key: 'no_director',
    label: 'No Director',
    stroke: '#2563eb',
  },
  {
    key: 'random',
    label: 'Random',
    stroke: '#f97316',
  },
  {
    key: 'director_based',
    label: 'Director',
    stroke: '#16a34a',
  },
];

const CHARTS = [
  {
    title: 'Gini over time',
    description: 'Wealth inequality by experiment strategy for each API response step.',
    metricKey: 'gini',
    yAxisLabel: 'Gini',
    yAxisProps: { domain: [0, 1], tickFormatter: formatDecimal },
    tooltipFormatter: (value, name) => [formatDecimal(value), name],
  },
  {
    title: 'Crime rate over time',
    description: 'Crime rate by experiment strategy for each API response step.',
    metricKey: 'crime_rate',
    yAxisLabel: 'Crime rate',
    yAxisProps: { allowDecimals: false },
    tooltipFormatter: (value, name) => [value, name],
  },
];

function formatDecimal(value) {
  return Number(value).toFixed(2);
}

function buildChartData(experiments, metricKey) {
  const maxSteps = Math.max(
    0,
    ...EXPERIMENT_LINES.map(
      ({ key }) => experiments[key]?.metrics_over_time?.length ?? 0,
    ),
  );

  return Array.from({ length: maxSteps }, (_, index) => {
    const row = { step: index + 1 };

    EXPERIMENT_LINES.forEach(({ key }) => {
      row[key] = experiments[key]?.metrics_over_time?.[index]?.[metricKey] ?? null;
    });

    return row;
  });
}

/**
 * Render experiment metrics returned by the API using Recharts.
 * @param {{experiments: Record<string, {metrics_over_time: Array<object>}>}} props
 */
export default function MetricsChart({ experiments }) {
  const hasExperimentMetrics = EXPERIMENT_LINES.some(
    ({ key }) => (experiments[key]?.metrics_over_time?.length ?? 0) > 0,
  );

  if (!hasExperimentMetrics) {
    return (
      <div className="dashboard-card flex min-h-80 items-center justify-center text-center">
        <p className="max-w-sm text-lg font-bold text-slate-500">Run an experiment to see metrics over time.</p>
      </div>
    );
  }

  return (
    <div className="grid gap-6" aria-label="Experiment comparison charts">
      {CHARTS.map(({ title, description, metricKey, yAxisLabel, yAxisProps, tooltipFormatter }) => (
        <article className="dashboard-card min-w-0" key={metricKey}>
          <div className="mb-4">
            <h2 className="text-xl font-black text-slate-950">{title}</h2>
            <p className="mt-1 text-sm font-semibold text-slate-500">{description}</p>
          </div>
          <ul className="chart-legend" aria-label={`${title} legend`}>
            {EXPERIMENT_LINES.map(({ key, label, stroke }) => (
              <li key={key}>
                <span className="legend-swatch" style={{ backgroundColor: stroke }} />
                {label}
              </li>
            ))}
          </ul>
          <ResponsiveContainer width="100%" height={300} initialDimension={{ width: 700, height: 300 }}>
            <LineChart
              data={buildChartData(experiments, metricKey)}
              margin={{ top: 10, right: 30, bottom: 20, left: 10 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="step"
                label={{ value: 'Step', position: 'insideBottom', offset: -10 }}
              />
              <YAxis
                {...yAxisProps}
                label={{ value: yAxisLabel, angle: -90, position: 'insideLeft' }}
              />
              <Tooltip formatter={tooltipFormatter} labelFormatter={(step) => `Step ${step}`} />
              {EXPERIMENT_LINES.map(({ key, label, stroke }) => (
                <Line
                  connectNulls
                  dataKey={key}
                  dot={{ r: 3 }}
                  isAnimationActive={false}
                  key={key}
                  name={label}
                  stroke={stroke}
                  strokeWidth={2}
                  type="monotone"
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </article>
      ))}
    </div>
  );
}
