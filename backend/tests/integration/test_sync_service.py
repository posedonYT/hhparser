from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import select

from app.core.config import get_settings
from app.db.models import MetricsDaily, VacancyRaw
from app.services.sync_service import SyncService


class StubHHClient:
    def __init__(self, items: list[dict]):
        self.items = items

    def search_vacancies(self, query_text, date_from, date_to):  # noqa: ANN001, D401
        return self.items


class StubCBRClient:
    def convert_to_rur(self, amount: Decimal, currency: str, for_date: date):  # noqa: ANN001
        if currency in {"RUR", "RUB"}:
            return amount
        return amount * Decimal("90")


def test_sync_idempotent_and_recalculates_metrics(db_session) -> None:
    settings = get_settings()

    source_items = [
        {
            "id": "10",
            "name": "Python Backend Engineer",
            "alternate_url": "https://hh.ru/vacancy/10",
            "employer": {"name": "Acme"},
            "published_at": "2026-03-30T10:00:00+0300",
            "experience": {"id": "between1And3"},
            "salary": {"from": 100000, "to": 200000, "currency": "RUR"},
        },
        {
            "id": "20",
            "name": "Python Backend Senior",
            "alternate_url": "https://hh.ru/vacancy/20",
            "employer": {"name": "Acme"},
            "published_at": "2026-03-29T10:00:00+0300",
            "experience": {"id": "between3And6"},
            "salary": None,
        },
    ]

    service = SyncService(
        session=db_session,
        settings=settings,
        hh_client=StubHHClient(source_items),
        cbr_client=StubCBRClient(),
    )

    first = service.sync("python_backend")
    second = service.sync("python_backend")

    assert first.status == "success"
    assert second.status == "success"

    vacancies = db_session.scalars(select(VacancyRaw).where(VacancyRaw.track == "python_backend")).all()
    assert len(vacancies) == 2

    metrics = db_session.scalars(select(MetricsDaily).where(MetricsDaily.track == "python_backend")).all()
    assert len(metrics) == 2

    by_bucket = {m.experience_bucket: m for m in metrics}
    assert by_bucket["between1And3"].vacancies_count == 1
    assert by_bucket["between1And3"].salary_count == 1
    assert float(by_bucket["between1And3"].avg_salary_rur) == 150000.0
