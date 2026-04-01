from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from dateutil.parser import isoparse

from app.db.models import ExperienceBucket

EXPERIENCE_MAP = {
    "noExperience": ExperienceBucket.no_experience,
    "between1And3": ExperienceBucket.between_1_and_3,
    "between3And6": ExperienceBucket.between_3_and_6,
    "moreThan6": ExperienceBucket.more_than_6,
}


@dataclass(frozen=True)
class SalaryNormalization:
    salary_from: Decimal | None
    salary_to: Decimal | None
    currency: str | None
    normalized_value: Decimal | None



def to_decimal(value: Any) -> Decimal | None:
    if value is None:
        return None
    return Decimal(str(value))



def normalize_salary(salary: dict[str, Any] | None) -> SalaryNormalization:
    if not salary:
        return SalaryNormalization(None, None, None, None)

    salary_from = to_decimal(salary.get("from"))
    salary_to = to_decimal(salary.get("to"))
    currency = salary.get("currency")

    normalized_value: Decimal | None
    if salary_from is not None and salary_to is not None:
        normalized_value = (salary_from + salary_to) / Decimal("2")
    elif salary_from is not None:
        normalized_value = salary_from
    elif salary_to is not None:
        normalized_value = salary_to
    else:
        normalized_value = None

    return SalaryNormalization(
        salary_from=salary_from,
        salary_to=salary_to,
        currency=currency,
        normalized_value=normalized_value,
    )



def map_experience_bucket(experience: dict[str, Any] | None) -> ExperienceBucket:
    if not experience:
        return ExperienceBucket.no_experience

    exp_id = experience.get("id")
    return EXPERIENCE_MAP.get(exp_id, ExperienceBucket.no_experience)



def parse_hh_datetime(value: str | None) -> datetime | None:
    if not value:
        return None

    dt = isoparse(value)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt
