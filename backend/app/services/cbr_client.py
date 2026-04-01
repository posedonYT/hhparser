from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP

import requests


class CBRClientError(RuntimeError):
    pass


class CBRClient:
    def __init__(
        self,
        base_url: str,
        timeout_seconds: int,
        max_fallback_days: int = 10,
        session: requests.Session | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.max_fallback_days = max_fallback_days
        self.session = session or requests.Session()
        self._daily_cache: dict[date, dict | None] = {}

    def convert_to_rur(self, amount: Decimal | None, currency: str | None, for_date: date) -> Decimal | None:
        if amount is None or not currency:
            return None

        currency_code = currency.upper()
        if currency_code in {"RUR", "RUB"}:
            return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        rate = self.get_rate(currency_code, for_date)
        return (amount * rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def get_rate(self, currency_code: str, for_date: date) -> Decimal:
        for delta in range(self.max_fallback_days + 1):
            current_date = for_date - timedelta(days=delta)
            rates = self._get_daily_rates(current_date)
            if not rates:
                continue

            valute = rates.get("Valute", {}).get(currency_code)
            if not valute:
                continue

            value = Decimal(str(valute["Value"]))
            nominal = Decimal(str(valute.get("Nominal", 1)))
            return value / nominal

        raise CBRClientError(f"Unable to find FX rate for {currency_code} up to {self.max_fallback_days} days back")

    def _get_daily_rates(self, for_date: date) -> dict | None:
        if for_date in self._daily_cache:
            return self._daily_cache[for_date]

        url = f"{self.base_url}/archive/{for_date:%Y/%m/%d}/daily_json.js"
        response = self.session.get(url, timeout=self.timeout_seconds)

        if response.status_code == 404:
            self._daily_cache[for_date] = None
            return None

        response.raise_for_status()
        payload = response.json()
        self._daily_cache[for_date] = payload
        return payload
