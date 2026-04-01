export type Track = 'python_backend' | 'swift';

export interface BreakdownItem {
  experience_bucket: 'noExperience' | 'between1And3' | 'between3And6' | 'moreThan6';
  experience_label: string;
  vacancies_count: number;
  salary_count: number;
  avg_salary_rur: number | null;
}

export interface LatestMetricsResponse {
  track: Track;
  snapshot_date: string | null;
  total_vacancies: number;
  salary_vacancies: number;
  salary_coverage: number;
  breakdown: BreakdownItem[];
}

export interface HistoryPoint {
  snapshot_date: string;
  vacancies_count: number;
  salary_vacancies: number;
  salary_coverage: number;
  avg_salary_rur: number | null;
}

export interface MetricsHistoryResponse {
  track: Track;
  days: number;
  points: HistoryPoint[];
}

export interface SyncTrackResult {
  track: Track;
  status: 'success' | 'failed';
  fetched: number;
  stored: number;
  with_salary: number;
  error?: string;
}

export interface SyncResponse {
  status: 'success' | 'failed' | 'partial_success';
  results: SyncTrackResult[];
}
