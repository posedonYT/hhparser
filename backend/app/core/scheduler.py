from __future__ import annotations

import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from apscheduler.schedulers.background import BackgroundScheduler

from app.core.config import get_settings
from app.db.session import get_session_factory
from app.services.sync_service import SyncService

logger = logging.getLogger(__name__)


def build_scheduler() -> BackgroundScheduler:
    settings = get_settings()
    scheduler = BackgroundScheduler(timezone=settings.timezone)

    def sync_all_tracks_job() -> None:
        session_factory = get_session_factory()
        with session_factory() as session:
            service = SyncService(session=session, settings=settings)
            result = service.sync("all")
            logger.info("Scheduled sync finished with status=%s", result.status)

    scheduler.add_job(
        sync_all_tracks_job,
        trigger="interval",
        minutes=settings.sync_interval_minutes,
        id="sync_all_tracks",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        next_run_time=datetime.now(ZoneInfo(settings.timezone)),
    )
    return scheduler
