interface KpiCardsProps {
  totalVacancies: number;
  salaryCoverage: number;
  salaryVacancies: number;
  snapshotDate: string | null;
}

function formatCoverage(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}

function formatDate(value: string | null): string {
  if (!value) {
    return 'нет данных';
  }
  return new Date(value).toLocaleDateString('ru-RU');
}

export function KpiCards({ totalVacancies, salaryCoverage, salaryVacancies, snapshotDate }: KpiCardsProps): JSX.Element {
  return (
    <section className="kpi-grid" aria-label="Ключевые метрики">
      <article className="kpi-card">
        <p className="kpi-label">Всего вакансий</p>
        <p className="kpi-value">{totalVacancies.toLocaleString('ru-RU')}</p>
      </article>

      <article className="kpi-card">
        <p className="kpi-label">Вакансий с зарплатой</p>
        <p className="kpi-value">{salaryVacancies.toLocaleString('ru-RU')}</p>
      </article>

      <article className="kpi-card">
        <p className="kpi-label">Покрытие зарплатой</p>
        <p className="kpi-value">{formatCoverage(salaryCoverage)}</p>
      </article>

      <article className="kpi-card">
        <p className="kpi-label">Актуальный срез</p>
        <p className="kpi-value">{formatDate(snapshotDate)}</p>
      </article>
    </section>
  );
}
