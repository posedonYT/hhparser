from datetime import date

from pydantic import BaseModel

from app.db.models import ExperienceBucket, Track


class ExperienceBreakdownItem(BaseModel):
    experience_bucket: ExperienceBucket
    experience_label: str
    vacancies_count: int
    salary_count: int
    avg_salary_rur: float | None


class LatestMetricsResponse(BaseModel):
    track: Track
    snapshot_date: date | None
    total_vacancies: int
    salary_vacancies: int
    salary_coverage: float
    breakdown: list[ExperienceBreakdownItem]


class HistoryPoint(BaseModel):
    snapshot_date: date
    vacancies_count: int
    salary_vacancies: int
    salary_coverage: float
    avg_salary_rur: float | None


class MetricsHistoryResponse(BaseModel):
    track: Track
    days: int
    points: list[HistoryPoint]
