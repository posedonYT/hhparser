from __future__ import annotations

from datetime import date, datetime, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.constants import EXPERIENCE_BUCKET_ORDER, EXPERIENCE_LABELS
from app.db.models import MetricsDaily, Track
from app.schemas.metrics import (
    ExperienceBreakdownItem,
    HistoryPoint,
    LatestMetricsResponse,
    MetricsHistoryResponse,
)


class MetricsService:
    def __init__(self, session: Session, timezone_name: str) -> None:
        self.session = session
        self.timezone_name = timezone_name

    def get_latest(self, track: Track) -> LatestMetricsResponse:
        latest_date = self.session.scalar(
            select(func.max(MetricsDaily.snapshot_date)).where(MetricsDaily.track == track.value)
        )

        rows_map: dict[str, MetricsDaily] = {}
        total_vacancies = 0
        salary_vacancies = 0

        if latest_date is not None:
            rows = self.session.scalars(
                select(MetricsDaily).where(
                    MetricsDaily.track == track.value,
                    MetricsDaily.snapshot_date == latest_date,
                )
            ).all()

            for row in rows:
                rows_map[row.experience_bucket] = row
                total_vacancies += row.vacancies_count
                salary_vacancies += row.salary_count

        coverage = (salary_vacancies / total_vacancies) if total_vacancies else 0.0
        breakdown = []

        for bucket in EXPERIENCE_BUCKET_ORDER:
            row = rows_map.get(bucket.value)
            breakdown.append(
                ExperienceBreakdownItem(
                    experience_bucket=bucket,
                    experience_label=EXPERIENCE_LABELS[bucket],
                    vacancies_count=row.vacancies_count if row else 0,
                    salary_count=row.salary_count if row else 0,
                    avg_salary_rur=float(row.avg_salary_rur) if row and row.avg_salary_rur is not None else None,
                )
            )

        return LatestMetricsResponse(
            track=track,
            snapshot_date=latest_date,
            total_vacancies=total_vacancies,
            salary_vacancies=salary_vacancies,
            salary_coverage=coverage,
            breakdown=breakdown,
        )

    def get_history(self, track: Track, days: int) -> MetricsHistoryResponse:
        days = max(1, days)
        today = datetime.now(ZoneInfo(self.timezone_name)).date()
        from_date = today - timedelta(days=days - 1)

        weighted_avg_salary = (
            func.sum(MetricsDaily.avg_salary_rur * MetricsDaily.salary_count)
            / func.nullif(func.sum(MetricsDaily.salary_count), 0)
        )

        rows = self.session.execute(
            select(
                MetricsDaily.snapshot_date,
                func.sum(MetricsDaily.vacancies_count).label("vacancies_count"),
                func.sum(MetricsDaily.salary_count).label("salary_count"),
                weighted_avg_salary.label("avg_salary_rur"),
            )
            .where(
                MetricsDaily.track == track.value,
                MetricsDaily.snapshot_date >= from_date,
                MetricsDaily.snapshot_date <= today,
            )
            .group_by(MetricsDaily.snapshot_date)
            .order_by(MetricsDaily.snapshot_date)
        ).all()

        row_map = {row.snapshot_date: row for row in rows}
        points: list[HistoryPoint] = []

        for offset in range(days):
            day = from_date + timedelta(days=offset)
            row = row_map.get(day)
            vacancies_count = int(row.vacancies_count) if row else 0
            salary_count = int(row.salary_count) if row else 0

            avg_salary_rur: float | None = None
            if row and row.avg_salary_rur is not None:
                avg_salary_rur = float(Decimal(row.avg_salary_rur))

            points.append(
                HistoryPoint(
                    snapshot_date=day,
                    vacancies_count=vacancies_count,
                    salary_vacancies=salary_count,
                    salary_coverage=(salary_count / vacancies_count) if vacancies_count else 0.0,
                    avg_salary_rur=avg_salary_rur,
                )
            )

        return MetricsHistoryResponse(track=track, days=days, points=points)
