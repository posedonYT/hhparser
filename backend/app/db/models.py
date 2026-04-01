from datetime import date, datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import Date, DateTime, Index, Integer, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Track(str, Enum):
    python_backend = "python_backend"
    swift = "swift"


class ExperienceBucket(str, Enum):
    no_experience = "noExperience"
    between_1_and_3 = "between1And3"
    between_3_and_6 = "between3And6"
    more_than_6 = "moreThan6"


class VacancyRaw(Base):
    __tablename__ = "vacancies_raw"
    __table_args__ = (
        UniqueConstraint("hh_id", "track", name="uq_vacancy_hh_id_track"),
        Index("ix_vacancy_track_published", "track", "published_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    hh_id: Mapped[str] = mapped_column(String(32), nullable=False)
    track: Mapped[str] = mapped_column(String(32), nullable=False)

    title: Mapped[str] = mapped_column(String(512), nullable=False)
    url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    employer: Mapped[str | None] = mapped_column(String(512), nullable=True)

    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    experience_bucket: Mapped[str] = mapped_column(String(32), nullable=False)

    salary_from: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    salary_to: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    salary_currency: Mapped[str | None] = mapped_column(String(8), nullable=True)
    salary_rur: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )


class MetricsDaily(Base):
    __tablename__ = "metrics_daily"
    __table_args__ = (
        UniqueConstraint("snapshot_date", "track", "experience_bucket", name="uq_metrics_snapshot_track_bucket"),
        Index("ix_metrics_track_snapshot", "track", "snapshot_date"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    snapshot_date: Mapped[date] = mapped_column(Date, nullable=False)
    track: Mapped[str] = mapped_column(String(32), nullable=False)
    experience_bucket: Mapped[str] = mapped_column(String(32), nullable=False)

    vacancies_count: Mapped[int] = mapped_column(Integer, nullable=False)
    salary_count: Mapped[int] = mapped_column(Integer, nullable=False)
    avg_salary_rur: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
