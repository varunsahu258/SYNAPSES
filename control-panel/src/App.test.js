import { render, screen } from '@testing-library/react';

import App from './App';

test('renders the run simulation control panel', () => {
  render(<App />);
  expect(screen.getByText(/Simulation Control Panel/i)).toBeInTheDocument();
  expect(screen.getByRole('button', { name: /Run Simulation/i })).toBeInTheDocument();
  expect(screen.getByText(/JSON result/i)).toBeInTheDocument();
});
