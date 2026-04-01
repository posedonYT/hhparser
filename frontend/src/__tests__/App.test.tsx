import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import App from '../App';

vi.mock('../components/ChartsPanel', () => ({
  ChartsPanel: () => <div data-testid="charts-panel" />
}));

const latestPayload = {
  track: 'python_backend',
  snapshot_date: '2026-04-01',
  total_vacancies: 12,
  salary_vacancies: 9,
  salary_coverage: 0.75,
  breakdown: [
    { experience_bucket: 'noExperience', experience_label: '0', vacancies_count: 2, salary_count: 1, avg_salary_rur: 120000 },
    {
      experience_bucket: 'between1And3',
      experience_label: '1-3',
      vacancies_count: 5,
      salary_count: 4,
      avg_salary_rur: 190000
    },
    {
      experience_bucket: 'between3And6',
      experience_label: '3-6',
      vacancies_count: 4,
      salary_count: 3,
      avg_salary_rur: 280000
    },
    {
      experience_bucket: 'moreThan6',
      experience_label: '6+',
      vacancies_count: 1,
      salary_count: 1,
      avg_salary_rur: 360000
    }
  ]
};

const historyPayload = {
  track: 'python_backend',
  days: 30,
  points: [
    { snapshot_date: '2026-03-31', vacancies_count: 11, salary_vacancies: 8, salary_coverage: 0.72, avg_salary_rur: 210000 },
    { snapshot_date: '2026-04-01', vacancies_count: 12, salary_vacancies: 9, salary_coverage: 0.75, avg_salary_rur: 220000 }
  ]
};

describe('App', () => {
  beforeEach(() => {
    vi.resetAllMocks();
    globalThis.fetch = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);

      if (url.includes('/metrics/latest')) {
        return new Response(JSON.stringify(latestPayload), { status: 200 });
      }

      if (url.includes('/metrics/history')) {
        return new Response(JSON.stringify(historyPayload), { status: 200 });
      }

      if (url.includes('/vacancies')) {
        return new Response(JSON.stringify({ track: 'python_backend', items: [] }), { status: 200 });
      }

      if (url.includes('/sync')) {
        return new Response(JSON.stringify({ status: 'success', results: [] }), { status: 200 });
      }

      return new Response('not found', { status: 404 });
    }) as typeof fetch;
  });

  it('renders dashboard and allows switching tabs', async () => {
    render(<App />);

    expect(await screen.findByText('Всего вакансий')).toBeInTheDocument();
    expect(screen.getAllByText('Python Backend').length).toBeGreaterThan(0);

    await userEvent.click(screen.getByRole('tab', { name: /Swift/i }));

    await waitFor(() => {
      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/metrics/latest?track=swift'),
        expect.any(Object)
      );
    });
  });

  it('runs manual refresh and calls sync endpoint', async () => {
    render(<App />);

    expect(await screen.findByRole('button', { name: /Обновить данные/i })).toBeInTheDocument();

    await userEvent.click(screen.getByRole('button', { name: /Обновить данные/i }));

    await waitFor(() => {
      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/sync?track=python_backend'),
        expect.any(Object)
      );
    });
  });
});
