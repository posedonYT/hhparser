from enum import Enum

from pydantic import BaseModel

from app.db.models import Track


class SyncTrackParam(str, Enum):
    python_backend = Track.python_backend.value
    swift = Track.swift.value
    all = "all"


class SyncTrackResult(BaseModel):
    track: Track
    status: str
    fetched: int
    stored: int
    with_salary: int
    error: str | None = None


class SyncResponse(BaseModel):
    status: str
    results: list[SyncTrackResult]
