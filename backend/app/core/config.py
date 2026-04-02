from functools import lru_cache
from typing import Self
from urllib.parse import quote_plus

from pydantic import AliasChoices, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "HH Analytics"
    api_v1_prefix: str = "/api/v1"

    # Если задан DATABASE_URL — используется он; иначе URL собирается из POSTGRES_* (один пароль с контейнером Postgres).
    database_url: str = Field(
        default="",
        validation_alias=AliasChoices("DATABASE_URL"),
    )
    postgres_user: str = Field(default="postgres", validation_alias=AliasChoices("POSTGRES_USER"))
    postgres_password: str = Field(default="postgres", validation_alias=AliasChoices("POSTGRES_PASSWORD"))
    postgres_host: str = Field(default="postgres", validation_alias=AliasChoices("POSTGRES_HOST"))
    postgres_port: int = Field(default=5432, validation_alias=AliasChoices("POSTGRES_PORT"))
    postgres_db: str = Field(default="hh_analytics", validation_alias=AliasChoices("POSTGRES_DB"))

    timezone: str = "Europe/Moscow"
    enable_scheduler: bool = True
    sync_interval_minutes: int = 60

    hh_base_url: str = "https://api.hh.ru"
    hh_area_id: int = 1
    hh_period_days: int = 30
    hh_per_page: int = 100
    hh_user_agent: str = "OZPraktika-HHAnalytics/1.0 (support@example.local)"

    cbr_base_url: str = "https://www.cbr-xml-daily.ru"
    request_timeout_seconds: int = 20

    frontend_origin: str = "http://localhost:5173,http://127.0.0.1:5173"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @model_validator(mode="after")
    def resolve_database_url(self) -> Self:
        direct = self.database_url.strip() if self.database_url else ""
        if direct:
            object.__setattr__(self, "database_url", direct)
            return self
        user = quote_plus(self.postgres_user)
        password = quote_plus(self.postgres_password)
        object.__setattr__(
            self,
            "database_url",
            f"postgresql+psycopg://{user}:{password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}",
        )
        return self


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
