from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.models import Track
from app.db.session import get_db
from app.schemas.metrics import LatestMetricsResponse, MetricsHistoryResponse
from app.services.metrics_service import MetricsService

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("/latest", response_model=LatestMetricsResponse)
def get_latest_metrics(
    track: Track = Query(..., description="python_backend or swift"),
    db: Session = Depends(get_db),
) -> LatestMetricsResponse:
    settings = get_settings()
    service = MetricsService(session=db, timezone_name=settings.timezone)
    return service.get_latest(track=track)


@router.get("/history", response_model=MetricsHistoryResponse)
def get_metrics_history(
    track: Track = Query(..., description="python_backend or swift"),
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
) -> MetricsHistoryResponse:
    settings = get_settings()
    service = MetricsService(session=db, timezone_name=settings.timezone)
    return service.get_history(track=track, days=days)
