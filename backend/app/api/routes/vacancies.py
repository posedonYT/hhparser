from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.models import Track
from app.db.session import get_db
from app.schemas.vacancies import VacancyListResponse
from app.services.vacancies_service import VacanciesService

router = APIRouter(prefix="/vacancies", tags=["vacancies"])


@router.get("", response_model=VacancyListResponse)
def list_vacancies(
    track: Track = Query(..., description="python_backend or swift"),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
) -> VacancyListResponse:
    service = VacanciesService(session=db)
    return service.list_for_track(track=track, limit=limit)
