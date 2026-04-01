from __future__ import annotations

from datetime import datetime, timezone

from app.services.hh_client import HHClient


class FakeResponse:
    def __init__(self, payload: dict):
        self.payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return self.payload


class FakeSession:
    def __init__(self, responses: dict[int, dict]):
        self.responses = responses
        self.requested_pages: list[int] = []

    def get(self, url: str, params: dict, timeout: int):  # noqa: ANN001
        self.requested_pages.append(params["page"])
        return FakeResponse(self.responses[params["page"]])


def test_hh_client_fetches_all_pages() -> None:
    session = FakeSession(
        {
            0: {"pages": 2, "items": [{"id": "1"}]},
            1: {"pages": 2, "items": [{"id": "2"}]},
        }
    )

    client = HHClient(
        base_url="https://api.hh.ru",
        area_id=1,
        per_page=100,
        timeout_seconds=10,
        session=session,
    )

    result = client.search_vacancies(
        query_text="Python backend",
        date_from=datetime(2026, 3, 1, tzinfo=timezone.utc),
        date_to=datetime(2026, 3, 30, tzinfo=timezone.utc),
    )

    assert len(result) == 2
    assert {item["id"] for item in result} == {"1", "2"}
    assert session.requested_pages == [0, 1]
