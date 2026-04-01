"""initial schema

Revision ID: 0001_init
Revises:
Create Date: 2026-04-01 17:10:00

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0001_init"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "vacancies_raw",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("hh_id", sa.String(length=32), nullable=False),
        sa.Column("track", sa.String(length=32), nullable=False),
        sa.Column("title", sa.String(length=512), nullable=False),
        sa.Column("url", sa.String(length=1024), nullable=True),
        sa.Column("employer", sa.String(length=512), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("experience_bucket", sa.String(length=32), nullable=False),
        sa.Column("salary_from", sa.Numeric(14, 2), nullable=True),
        sa.Column("salary_to", sa.Numeric(14, 2), nullable=True),
        sa.Column("salary_currency", sa.String(length=8), nullable=True),
        sa.Column("salary_rur", sa.Numeric(14, 2), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("hh_id", "track", name="uq_vacancy_hh_id_track"),
    )
    op.create_index("ix_vacancy_track_published", "vacancies_raw", ["track", "published_at"], unique=False)

    op.create_table(
        "metrics_daily",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("snapshot_date", sa.Date(), nullable=False),
        sa.Column("track", sa.String(length=32), nullable=False),
        sa.Column("experience_bucket", sa.String(length=32), nullable=False),
        sa.Column("vacancies_count", sa.Integer(), nullable=False),
        sa.Column("salary_count", sa.Integer(), nullable=False),
        sa.Column("avg_salary_rur", sa.Numeric(14, 2), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("snapshot_date", "track", "experience_bucket", name="uq_metrics_snapshot_track_bucket"),
    )
    op.create_index("ix_metrics_track_snapshot", "metrics_daily", ["track", "snapshot_date"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_metrics_track_snapshot", table_name="metrics_daily")
    op.drop_table("metrics_daily")
    op.drop_index("ix_vacancy_track_published", table_name="vacancies_raw")
    op.drop_table("vacancies_raw")
