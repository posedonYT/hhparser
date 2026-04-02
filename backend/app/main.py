from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError

from app.api.router import api_router
from app.core.config import get_settings
from app.core.scheduler import build_scheduler


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name)

    @app.exception_handler(OperationalError)
    async def database_operational_error_handler(
        _request: Request,
        _exc: OperationalError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=503,
            content={
                "detail": (
                    "База данных недоступна или неверные учётные данные. "
                    "Проверьте POSTGRES_PASSWORD / DATABASE_URL и при смене пароля пересоздайте том PostgreSQL."
                )
            },
        )

    cors_origins = [
        origin.strip()
        for origin in settings.frontend_origin.split(",")
        if origin.strip()
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix=settings.api_v1_prefix)

    @app.on_event("startup")
    def on_startup() -> None:
        if not settings.enable_scheduler:
            return
        scheduler = build_scheduler()
        scheduler.start()
        app.state.scheduler = scheduler

    @app.on_event("shutdown")
    def on_shutdown() -> None:
        scheduler = getattr(app.state, "scheduler", None)
        if scheduler:
            scheduler.shutdown(wait=False)

    return app


app = create_app()
