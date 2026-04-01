from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "HH Analytics"
    api_v1_prefix: str = "/api/v1"

    database_url: str = "postgresql+psycopg://postgres:postgres@postgres:5432/hh_analytics"

    timezone: str = "Europe/Moscow"
    enable_scheduler: bool = True
    sync_interval_minutes: int = 60

    hh_base_url: str = "https://api.hh.ru"
    hh_area_id: int = 1
    hh_period_days: int = 30
    hh_per_page: int = 100

    cbr_base_url: str = "https://www.cbr-xml-daily.ru"
    request_timeout_seconds: int = 20

    frontend_origin: str = "http://localhost:5173"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
