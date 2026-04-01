from __future__ import annotations

from app.db.models import Track
from app.services.sync_service import SyncSummary, TrackSyncStats


def test_sync_endpoint_contract(client, monkeypatch) -> None:
    def fake_sync(self, track_param: str = "all") -> SyncSummary:  # noqa: ANN001
        return SyncSummary(
            status="success",
            results=[
                TrackSyncStats(
                    track=Track.python_backend,
                    status="success",
                    fetched=10,
                    stored=8,
                    with_salary=5,
                )
            ],
        )

    monkeypatch.setattr("app.services.sync_service.SyncService.sync", fake_sync)

    response = client.post("/api/v1/sync", params={"track": "python_backend"})
    assert response.status_code == 200

    body = response.json()
    assert body["status"] == "success"
    assert body["results"][0]["track"] == "python_backend"
    assert body["results"][0]["fetched"] == 10
