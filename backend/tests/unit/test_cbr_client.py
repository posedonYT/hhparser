from __future__ import annotations

from datetime import date
from decimal import Decimal

import requests

from app.services.cbr_client import CBRClient


class FakeResponse:
    def __init__(self, status_code: int, payload: dict | None = None):
        self.status_code = status_code
        self._payload = payload or {}

    def raise_for_status(self) -> None:
        if self.status_code >= 400 and self.status_code != 404:
            raise requests.HTTPError(f"HTTP {self.status_code}")

    def json(self) -> dict:
        return self._payload


class FakeSession:
    def __init__(self, responses: dict[str, FakeResponse]):
        self.responses = responses

    def get(self, url: str, timeout: int):  # noqa: ANN001
        return self.responses[url]


def test_cbr_fallback_to_previous_day_rate() -> None:
    target_day = date(2026, 3, 30)
    fallback_day = date(2026, 3, 29)

    base_url = "https://www.cbr-xml-daily.ru"
    missing_url = f"{base_url}/archive/{target_day:%Y/%m/%d}/daily_json.js"
    fallback_url = f"{base_url}/archive/{fallback_day:%Y/%m/%d}/daily_json.js"

    session = FakeSession(
        {
            missing_url: FakeResponse(404),
            fallback_url: FakeResponse(
                200,
                {
                    "Valute": {
                        "USD": {
                            "Value": 90,
                            "Nominal": 1,
                        }
                    }
                },
            ),
        }
    )

    client = CBRClient(base_url=base_url, timeout_seconds=10, max_fallback_days=2, session=session)
    converted = client.convert_to_rur(Decimal("100"), "USD", target_day)

    assert converted == Decimal("9000.00")


def test_cbr_rub_passthrough() -> None:
    client = CBRClient(base_url="https://www.cbr-xml-daily.ru", timeout_seconds=10)
    assert client.convert_to_rur(Decimal("123.456"), "RUB", date(2026, 3, 30)) == Decimal("123.46")
