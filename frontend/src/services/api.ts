import type {
  LatestMetricsResponse,
  MetricsHistoryResponse,
  SyncResponse,
  Track,
  VacancyListResponse
} from '../types/api';

/** Относительный путь + proxy в Vite: один origin с UI, без CORS (localhost vs 127.0.0.1 и Docker). */
const API_BASE = import.meta.env.VITE_API_BASE_URL ?? '/api/v1';

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      'Content-Type': 'application/json'
    },
    ...init
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`Request failed (${response.status}): ${text || response.statusText}`);
  }

  return (await response.json()) as T;
}

export function fetchLatestMetrics(track: Track): Promise<LatestMetricsResponse> {
  return request<LatestMetricsResponse>(`/metrics/latest?track=${track}`);
}

export function fetchMetricsHistory(track: Track, days = 30): Promise<MetricsHistoryResponse> {
  return request<MetricsHistoryResponse>(`/metrics/history?track=${track}&days=${days}`);
}

export function triggerSync(track: Track): Promise<SyncResponse> {
  return request<SyncResponse>(`/sync?track=${track}`, {
    method: 'POST'
  });
}

export function fetchVacancies(track: Track, limit = 50): Promise<VacancyListResponse> {
  return request<VacancyListResponse>(`/vacancies?track=${track}&limit=${limit}`);
}
