from __future__ import annotations

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.db.models import Track, VacancyRaw
from app.schemas.vacancies import VacancyItem, VacancyListResponse


class VacanciesService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_for_track(self, track: Track, limit: int) -> VacancyListResponse:
        limit = max(1, min(limit, 100))
        rows = self.session.scalars(
            select(VacancyRaw)
            .where(VacancyRaw.track == track.value)
            .order_by(desc(VacancyRaw.published_at))
            .limit(limit)
        ).all()

        items = [
            VacancyItem(
                hh_id=row.hh_id,
                title=row.title,
                employer=row.employer,
                url=row.url,
            )
            for row in rows
        ]

        return VacancyListResponse(track=track, items=items)
