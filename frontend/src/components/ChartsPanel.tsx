import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from 'recharts';

import type { BreakdownItem, HistoryPoint } from '../types/api';

interface ChartsPanelProps {
  breakdown: BreakdownItem[];
  history: HistoryPoint[];
}

function formatSalary(value: number | null): string {
  if (value === null) {
    return '—';
  }
  return `${Math.round(value).toLocaleString('ru-RU')} ₽`;
}

export function ChartsPanel({ breakdown, history }: ChartsPanelProps): JSX.Element {
  const salaryByGradeData = breakdown.map((item) => ({
    grade: item.experience_label,
    salary: item.avg_salary_rur ?? 0,
    rawSalary: item.avg_salary_rur
  }));

  const vacanciesTrendData = history.map((point) => ({
    day: new Date(point.snapshot_date).toLocaleDateString('ru-RU', { month: 'short', day: 'numeric' }),
    vacancies: point.vacancies_count
  }));

  return (
    <section className="charts-grid">
      <article className="chart-card">
        <h3>Средняя зарплата по опыту</h3>
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={salaryByGradeData}>
            <CartesianGrid strokeDasharray="4 4" stroke="rgba(23, 23, 23, 0.1)" />
            <XAxis dataKey="grade" tickLine={false} axisLine={false} />
            <YAxis tickLine={false} axisLine={false} width={88} tickFormatter={(v) => `${Math.round(v / 1000)}k`} />
            <Tooltip formatter={(value: number, _name, payload) => formatSalary(payload.payload.rawSalary)} />
            <Bar dataKey="salary" fill="url(#salaryGradient)" radius={[8, 8, 0, 0]} />
            <defs>
              <linearGradient id="salaryGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#f08c3b" stopOpacity={0.95} />
                <stop offset="100%" stopColor="#e05f2d" stopOpacity={0.9} />
              </linearGradient>
            </defs>
          </BarChart>
        </ResponsiveContainer>
      </article>

      <article className="chart-card">
        <h3>Динамика количества вакансий</h3>
        <ResponsiveContainer width="100%" height={280}>
          <LineChart data={vacanciesTrendData}>
            <CartesianGrid strokeDasharray="4 4" stroke="rgba(23, 23, 23, 0.1)" />
            <XAxis dataKey="day" tickLine={false} axisLine={false} minTickGap={24} />
            <YAxis tickLine={false} axisLine={false} width={52} />
            <Tooltip />
            <Line type="monotone" dataKey="vacancies" stroke="#0d8b8b" strokeWidth={3} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </article>
    </section>
  );
}
