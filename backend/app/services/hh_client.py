from __future__ import annotations

import requests


class HHClient:
    def __init__(
        self,
        base_url: str,
        area_id: int,
        per_page: int,
        timeout_seconds: int,
        user_agent: str,
        session: requests.Session | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.area_id = area_id
        self.per_page = per_page
        self.timeout_seconds = timeout_seconds
        self.session = session or requests.Session()
        if "User-Agent" not in self.session.headers:
            self.session.headers["User-Agent"] = user_agent

    def search_vacancies(self, query_text: str, period_days: int) -> list[dict]:
        """Ищет вакансии за последние ``period_days`` дней (параметр ``period`` в API HH)."""
        items: list[dict] = []
        page = 0
        total_pages = 1

        while page < total_pages:
            params = {
                "text": query_text,
                "area": self.area_id,
                "period": max(1, int(period_days)),
                "per_page": self.per_page,
                "page": page,
            }
            response = self.session.get(f"{self.base_url}/vacancies", params=params, timeout=self.timeout_seconds)
            response.raise_for_status()
            payload = response.json()

            items.extend(payload.get("items", []))
            total_pages = int(payload.get("pages", 0))

            if total_pages <= 0 or page >= total_pages - 1:
                break
            page += 1

        return items
