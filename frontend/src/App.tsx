import { useCallback, useEffect, useState } from 'react';

import { ChartsPanel } from './components/ChartsPanel';
import { KpiCards } from './components/KpiCards';
import { TrackTabs } from './components/TrackTabs';
import { fetchLatestMetrics, fetchMetricsHistory, triggerSync } from './services/api';
import type { LatestMetricsResponse, MetricsHistoryResponse, Track } from './types/api';

const EMPTY_LATEST: LatestMetricsResponse = {
  track: 'python_backend',
  snapshot_date: null,
  total_vacancies: 0,
  salary_vacancies: 0,
  salary_coverage: 0,
  breakdown: [
    { experience_bucket: 'noExperience', experience_label: '0', vacancies_count: 0, salary_count: 0, avg_salary_rur: null },
    {
      experience_bucket: 'between1And3',
      experience_label: '1-3',
      vacancies_count: 0,
      salary_count: 0,
      avg_salary_rur: null
    },
    {
      experience_bucket: 'between3And6',
      experience_label: '3-6',
      vacancies_count: 0,
      salary_count: 0,
      avg_salary_rur: null
    },
    {
      experience_bucket: 'moreThan6',
      experience_label: '6+',
      vacancies_count: 0,
      salary_count: 0,
      avg_salary_rur: null
    }
  ]
};

const EMPTY_HISTORY: MetricsHistoryResponse = {
  track: 'python_backend',
  days: 30,
  points: []
};

const trackTitles: Record<Track, string> = {
  python_backend: 'Python Backend',
  swift: 'Swift'
};

export default function App(): JSX.Element {
  const [activeTrack, setActiveTrack] = useState<Track>('python_backend');
  const [latestMetrics, setLatestMetrics] = useState<LatestMetricsResponse>(EMPTY_LATEST);
  const [historyMetrics, setHistoryMetrics] = useState<MetricsHistoryResponse>(EMPTY_HISTORY);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const loadData = useCallback(async (track: Track) => {
    setLoading(true);
    setErrorMessage(null);

    try {
      const [latest, history] = await Promise.all([fetchLatestMetrics(track), fetchMetricsHistory(track, 30)]);
      setLatestMetrics(latest);
      setHistoryMetrics(history);
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Не удалось загрузить данные';
      setErrorMessage(message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadData(activeTrack);
  }, [activeTrack, loadData]);

  const handleRefresh = async (): Promise<void> => {
    setRefreshing(true);
    setErrorMessage(null);

    try {
      await triggerSync(activeTrack);
      await loadData(activeTrack);
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Ошибка запуска обновления';
      setErrorMessage(message);
    } finally {
      setRefreshing(false);
    }
  };

  return (
    <main className="page">
      <section className="hero">
        <div>
          <p className="hero-kicker">HH Analytics</p>
          <h1>Рынок вакансий: Backend и Swift</h1>
          <p className="hero-subtitle">
            Отдельная аналитика по направлениям с hourly обновлением и метриками зарплат по опыту.
          </p>
        </div>

        <button className="refresh-button" onClick={() => void handleRefresh()} disabled={refreshing || loading}>
          {refreshing ? 'Обновляем…' : 'Обновить данные'}
        </button>
      </section>

      <TrackTabs activeTrack={activeTrack} onChange={setActiveTrack} />

      <section className="section-title-wrap">
        <h2>{trackTitles[activeTrack]}</h2>
      </section>

      {loading ? (
        <div className="state-card">Загрузка данных…</div>
      ) : errorMessage ? (
        <div className="state-card error">
          <p>{errorMessage}</p>
          <button className="inline-button" onClick={() => void loadData(activeTrack)}>
            Повторить
          </button>
        </div>
      ) : (
        <>
          <KpiCards
            totalVacancies={latestMetrics.total_vacancies}
            salaryCoverage={latestMetrics.salary_coverage}
            salaryVacancies={latestMetrics.salary_vacancies}
            snapshotDate={latestMetrics.snapshot_date}
          />
          <ChartsPanel breakdown={latestMetrics.breakdown} history={historyMetrics.points} />
        </>
      )}
    </main>
  );
}
