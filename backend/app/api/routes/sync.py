from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db
from app.schemas.sync import SyncResponse, SyncTrackParam, SyncTrackResult
from app.services.sync_service import SyncService

router = APIRouter(prefix="/sync", tags=["sync"])


@router.post("", response_model=SyncResponse)
def run_sync(
    track: SyncTrackParam = Query(default=SyncTrackParam.all),
    db: Session = Depends(get_db),
) -> SyncResponse:
    settings = get_settings()
    service = SyncService(session=db, settings=settings)
    summary = service.sync(track.value)

    return SyncResponse(
        status=summary.status,
        results=[
            SyncTrackResult(
                track=result.track,
                status=result.status,
                fetched=result.fetched,
                stored=result.stored,
                with_salary=result.with_salary,
                error=result.error,
            )
            for result in summary.results
        ],
    )
