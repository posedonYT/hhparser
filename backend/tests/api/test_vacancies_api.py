from __future__ import annotations

from datetime import datetime, timezone

from app.db.models import VacancyRaw


def test_vacancies_list_ordered_and_limited(client, db_session) -> None:
    base = datetime(2026, 4, 1, 12, 0, 0, tzinfo=timezone.utc)
    for i in range(3):
        db_session.add(
            VacancyRaw(
                hh_id=f"id-{i}",
                track="python_backend",
                title=f"Вакансия {i}",
                url=f"https://hh.ru/vacancy/{i}",
                employer=f"Компания {i}",
                published_at=base.replace(hour=12 + i),
                experience_bucket="between1And3",
            )
        )
    db_session.commit()

    resp = client.get("/api/v1/vacancies", params={"track": "python_backend", "limit": 2})
    assert resp.status_code == 200
    data = resp.json()
    assert data["track"] == "python_backend"
    assert len(data["items"]) == 2
    assert data["items"][0]["hh_id"] == "id-2"
    assert data["items"][0]["title"] == "Вакансия 2"
    assert data["items"][0]["employer"] == "Компания 2"
    assert data["items"][0]["url"] == "https://hh.ru/vacancy/2"
