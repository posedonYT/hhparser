from __future__ import annotations

from datetime import datetime, timedelta

from app.db.models import MetricsDaily


def test_metrics_latest_and_history(client, db_session) -> None:
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)

    db_session.add_all(
        [
            MetricsDaily(
                snapshot_date=today,
                track="python_backend",
                experience_bucket="between1And3",
                vacancies_count=4,
                salary_count=3,
                avg_salary_rur=180000,
            ),
            MetricsDaily(
                snapshot_date=today,
                track="python_backend",
                experience_bucket="between3And6",
                vacancies_count=2,
                salary_count=2,
                avg_salary_rur=260000,
            ),
            MetricsDaily(
                snapshot_date=yesterday,
                track="python_backend",
                experience_bucket="between1And3",
                vacancies_count=3,
                salary_count=2,
                avg_salary_rur=170000,
            ),
        ]
    )
    db_session.commit()

    latest_resp = client.get("/api/v1/metrics/latest", params={"track": "python_backend"})
    assert latest_resp.status_code == 200
    latest = latest_resp.json()

    assert latest["track"] == "python_backend"
    assert latest["total_vacancies"] == 6
    assert latest["salary_vacancies"] == 5
    assert len(latest["breakdown"]) == 4

    history_resp = client.get("/api/v1/metrics/history", params={"track": "python_backend", "days": 2})
    assert history_resp.status_code == 200
    history = history_resp.json()

    assert history["track"] == "python_backend"
    assert history["days"] == 2
    assert len(history["points"]) == 2
    assert history["points"][-1]["vacancies_count"] == 6
