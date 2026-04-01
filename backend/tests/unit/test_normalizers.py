from decimal import Decimal

from app.db.models import ExperienceBucket
from app.services.normalizers import map_experience_bucket, normalize_salary


def test_map_experience_bucket() -> None:
    assert map_experience_bucket({"id": "between1And3"}) == ExperienceBucket.between_1_and_3
    assert map_experience_bucket({"id": "between3And6"}) == ExperienceBucket.between_3_and_6
    assert map_experience_bucket({"id": "unknown"}) == ExperienceBucket.no_experience


def test_normalize_salary_midpoint() -> None:
    result = normalize_salary({"from": 100000, "to": 200000, "currency": "RUR"})

    assert result.salary_from == Decimal("100000")
    assert result.salary_to == Decimal("200000")
    assert result.currency == "RUR"
    assert result.normalized_value == Decimal("150000")


def test_normalize_salary_single_bound() -> None:
    result_from = normalize_salary({"from": 170000, "to": None, "currency": "RUR"})
    result_to = normalize_salary({"from": None, "to": 190000, "currency": "RUR"})

    assert result_from.normalized_value == Decimal("170000")
    assert result_to.normalized_value == Decimal("190000")
