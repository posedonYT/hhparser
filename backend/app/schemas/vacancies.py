from pydantic import BaseModel

from app.db.models import Track


class VacancyItem(BaseModel):
    hh_id: str
    title: str
    employer: str | None
    url: str | None


class VacancyListResponse(BaseModel):
    track: Track
    items: list[VacancyItem]
