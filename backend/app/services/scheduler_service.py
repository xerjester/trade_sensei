"""Daily DFD 2.2 job: refresh external prices/news and store D3/D4/D7."""
import atexit
import logging
import os
from typing import Any

from app.services.scraper_service import run_batch_scrape

logger = logging.getLogger(__name__)
# Kept as ``Any`` because APScheduler is imported lazily below.  This lets an
# older Docker image boot and report a clear warning instead of failing Flask
# imports before the image has been rebuilt with the new requirement.
_scheduler: Any = None


def _daily_market_refresh(app) -> None:
    """Run inside an application context because the scraper writes SQLAlchemy models."""
    with app.app_context():
        try:
            run_batch_scrape()
        except Exception:
            logger.exception('Scheduled market/news refresh failed')


def start_scheduler(app) -> None:
    """Schedule one midnight Asia/Bangkok refresh per backend process.

    Werkzeug's debug reloader starts a parent and child process; the parent is
    intentionally skipped so it cannot run the daily pipeline twice.
    """
    global _scheduler
    if _scheduler is not None:
        return
    debug_reloader = app.debug or os.environ.get('FLASK_DEBUG') == '1'
    if debug_reloader and os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        return

    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        from apscheduler.triggers.cron import CronTrigger
    except ImportError:
        logger.warning(
            'APScheduler is not installed; daily market/news refresh is disabled. '
            'Rebuild the backend image after updating requirements.txt.'
        )
        return

    _scheduler = BackgroundScheduler(timezone='Asia/Bangkok')
    _scheduler.add_job(
        lambda: _daily_market_refresh(app),
        CronTrigger(hour=0, minute=0, timezone='Asia/Bangkok'),
        id='daily_market_news_refresh',
        replace_existing=True,
        misfire_grace_time=3600,
    )
    _scheduler.start()
    atexit.register(lambda: _scheduler.shutdown(wait=False) if _scheduler else None)
