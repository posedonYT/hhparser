from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.core.constants import TRACK_QUERY_MAP
from app.db.models import ExperienceBucket, MetricsDaily, Track, VacancyRaw
from app.services.cbr_client import CBRClient
from app.services.hh_client import HHClient
from app.services.normalizers import map_experience_bucket, normalize_salary, parse_hh_datetime

logger = logging.getLogger(__name__)


@dataclass
class NormalizedVacancy:
    hh_id: str
    track: Track
    title: str
    url: str | None
    employer: str | None
    published_at: datetime
    experience_bucket: ExperienceBucket
    salary_from: Decimal | None
    salary_to: Decimal | None
    salary_currency: str | None
    salary_rur: Decimal | None


@dataclass
class TrackSyncStats:
    track: Track
    status: str
    fetched: int = 0
    stored: int = 0
    with_salary: int = 0
    error: str | None = None


@dataclass
class SyncSummary:
    status: str
    results: list[TrackSyncStats]


class SyncService:
    def __init__(
        self,
        session: Session,
        settings: Settings,
        hh_client: HHClient | None = None,
        cbr_client: CBRClient | None = None,
    ) -> None:
        self.session = session
        self.settings = settings
        self.hh_client = hh_client or HHClient(
            base_url=settings.hh_base_url,
            area_id=settings.hh_area_id,
            per_page=settings.hh_per_page,
            timeout_seconds=settings.request_timeout_seconds,
            user_agent=settings.hh_user_agent,
        )
        self.cbr_client = cbr_client or CBRClient(
            base_url=settings.cbr_base_url,
            timeout_seconds=settings.request_timeout_seconds,
        )

    def sync(self, track_param: str = "all") -> SyncSummary:
        if track_param == "all":
            tracks = list(TRACK_QUERY_MAP.keys())
        else:
            tracks = [Track(track_param)]

        results: list[TrackSyncStats] = []

        for track in tracks:
            try:
                result = self._sync_track(track)
                results.append(result)
            except Exception as exc:  # noqa: BLE001
                logger.exception("Sync failed for track=%s", track.value)
                self.session.rollback()
                results.append(
                    TrackSyncStats(
                        track=track,
                        status="failed",
                        error=str(exc),
                    )
                )

        failed_count = len([r for r in results if r.status == "failed"])
        if failed_count == 0:
            status = "success"
        elif failed_count == len(results):
            status = "failed"
        else:
            status = "partial_success"

        return SyncSummary(status=status, results=results)

    def _sync_track(self, track: Track) -> TrackSyncStats:
        tz_moscow = ZoneInfo(self.settings.timezone)
        now_moscow = datetime.now(tz_moscow)
        query_text = TRACK_QUERY_MAP[track]

        # Начало календарного окна (как у period в HH), чтобы не выкидывать вакансии из выдачи API
        # из‑за сравнения published_at с «сейчас минус N суток по часам».
        window_start_moscow = (now_moscow - timedelta(days=self.settings.hh_period_days)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        cutoff_utc = window_start_moscow.astimezone(ZoneInfo("UTC"))

        fetched_items = self.hh_client.search_vacancies(
            query_text=query_text,
            period_days=self.settings.hh_period_days,
        )

        normalized_map: dict[str, NormalizedVacancy] = {}
        with_salary = 0

        for item in fetched_items:
            normalized = self._normalize_vacancy(item=item, track=track)
            if normalized is None:
                continue
            normalized_map[normalized.hh_id] = normalized
            if normalized.salary_rur is not None:
                with_salary += 1

        normalized_items = list(normalized_map.values())
        incoming_ids = [item.hh_id for item in normalized_items]

        existing_by_hh_id: dict[str, VacancyRaw] = {}
        if incoming_ids:
            existing_rows = self.session.scalars(
                select(VacancyRaw).where(
                    VacancyRaw.track == track.value,
                    VacancyRaw.hh_id.in_(incoming_ids),
                )
            ).all()
            existing_by_hh_id = {row.hh_id: row for row in existing_rows}

        for vacancy in normalized_items:
            existing = existing_by_hh_id.get(vacancy.hh_id)
            if existing:
                existing.title = vacancy.title
                existing.url = vacancy.url
                existing.employer = vacancy.employer
                existing.published_at = vacancy.published_at
                existing.experience_bucket = vacancy.experience_bucket.value
                existing.salary_from = vacancy.salary_from
                existing.salary_to = vacancy.salary_to
                existing.salary_currency = vacancy.salary_currency
                existing.salary_rur = vacancy.salary_rur
            else:
                self.session.add(
                    VacancyRaw(
                        hh_id=vacancy.hh_id,
                        track=vacancy.track.value,
                        title=vacancy.title,
                        url=vacancy.url,
                        employer=vacancy.employer,
                        published_at=vacancy.published_at,
                        experience_bucket=vacancy.experience_bucket.value,
                        salary_from=vacancy.salary_from,
                        salary_to=vacancy.salary_to,
                        salary_currency=vacancy.salary_currency,
                        salary_rur=vacancy.salary_rur,
                    )
                )

        if incoming_ids:
            self.session.execute(
                delete(VacancyRaw).where(
                    VacancyRaw.track == track.value,
                    ~VacancyRaw.hh_id.in_(incoming_ids),
                )
            )
        else:
            self.session.execute(delete(VacancyRaw).where(VacancyRaw.track == track.value))

        self.session.execute(
            delete(VacancyRaw).where(
                VacancyRaw.track == track.value,
                VacancyRaw.published_at < cutoff_utc,
            )
        )

        self._recalculate_metrics(track=track, snapshot_date=now_moscow.date(), cutoff_datetime=cutoff_utc)
        self.session.commit()

        return TrackSyncStats(
            track=track,
            status="success",
            fetched=len(fetched_items),
            stored=len(normalized_items),
            with_salary=with_salary,
        )

    def _normalize_vacancy(self, item: dict, track: Track) -> NormalizedVacancy | None:
        hh_id_raw = item.get("id")
        published_at = parse_hh_datetime(item.get("published_at"))

        if not hh_id_raw or not published_at:
            return None

        salary_data = normalize_salary(item.get("salary"))
        salary_currency = salary_data.currency

        salary_rur = None
        if salary_data.normalized_value is not None and salary_currency:
            try:
                salary_rur = self.cbr_client.convert_to_rur(
                    amount=salary_data.normalized_value,
                    currency=salary_currency,
                    for_date=published_at.date(),
                )
            except Exception:  # noqa: BLE001
                logger.exception(
                    "Salary conversion failed for vacancy_id=%s currency=%s",
                    hh_id_raw,
                    salary_currency,
                )
                salary_rur = None

        experience_bucket = map_experience_bucket(item.get("experience"))
        employer = None
        if isinstance(item.get("employer"), dict):
            employer = item["employer"].get("name")

        return NormalizedVacancy(
            hh_id=str(hh_id_raw),
            track=track,
            title=item.get("name") or "(no title)",
            url=item.get("alternate_url"),
            employer=employer,
            published_at=published_at,
            experience_bucket=experience_bucket,
            salary_from=salary_data.salary_from,
            salary_to=salary_data.salary_to,
            salary_currency=salary_currency,
            salary_rur=salary_rur,
        )

    def _recalculate_metrics(self, track: Track, snapshot_date: date, cutoff_datetime: datetime) -> None:
        self.session.execute(
            delete(MetricsDaily).where(
                MetricsDaily.track == track.value,
                MetricsDaily.snapshot_date == snapshot_date,
            )
        )

        rows = self.session.execute(
            select(
                VacancyRaw.experience_bucket,
                func.count(VacancyRaw.id).label("vacancies_count"),
                func.count(VacancyRaw.salary_rur).label("salary_count"),
                func.avg(VacancyRaw.salary_rur).label("avg_salary_rur"),
            )
            .where(
                VacancyRaw.track == track.value,
                VacancyRaw.published_at >= cutoff_datetime,
            )
            .group_by(VacancyRaw.experience_bucket)
        ).all()

        for row in rows:
            self.session.add(
                MetricsDaily(
                    snapshot_date=snapshot_date,
                    track=track.value,
                    experience_bucket=row.experience_bucket,
                    vacancies_count=int(row.vacancies_count),
                    salary_count=int(row.salary_count),
                    avg_salary_rur=row.avg_salary_rur,
                )
            )
