import type { VacancyListItem } from '../types/api';

interface VacancyListProps {
  items: VacancyListItem[];
}

export function VacancyList({ items }: VacancyListProps): JSX.Element {
  return (
    <section className="vacancy-section" aria-label="Список вакансий">
      <h3 className="vacancy-section-title">Вакансии в срезе</h3>
      {items.length === 0 ? (
        <p className="vacancy-empty">Нет вакансий — обновите данные с hh.ru.</p>
      ) : (
        <ul className="vacancy-list">
          {items.map((item) => (
            <li key={item.hh_id} className="vacancy-card">
              <p className="vacancy-title">{item.title}</p>
              <p className="vacancy-employer">{item.employer ?? 'Компания не указана'}</p>
              {item.url ? (
                <a className="vacancy-link" href={item.url} target="_blank" rel="noopener noreferrer">
                  Открыть на hh.ru
                </a>
              ) : (
                <span className="vacancy-link-muted">Ссылка недоступна</span>
              )}
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
