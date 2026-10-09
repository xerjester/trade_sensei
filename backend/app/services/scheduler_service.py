# ระบบตั้งเวลาทำงานอัตโนมัติ (Scheduler) — ดึงราคาหุ้นและข่าวสารรอบเที่ยงคืนทุกวัน
import atexit
import logging
import os
from typing import Any

from app.services.scraper_service import run_batch_scrape

logger = logging.getLogger(__name__)

# ตัวแปรเก็บอินสแตนซ์ของ APScheduler สำหรับรันงานเบื้องหลัง
_scheduler: Any = None


# ฟังก์ชันดึงข้อมูลราคาและข่าวสารตลาดประจำวัน (รันภายใต้ Flask Application Context)
def _daily_market_refresh(app) -> None:
    with app.app_context():
        try:
            run_batch_scrape()
        except Exception:
            logger.exception('ระบบตั้งเวลาดึงข้อมูลตลาด/ข่าวสารอัตโนมัติขัดข้อง')


# เริ่มต้นระบบตั้งเวลา Background Scheduler ให้ทำงานอัตโนมัติทุกเที่ยงคืน (เวลาประเทศไทย)
def start_scheduler(app) -> None:
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
            'ไม่พบแพ็กเกจ APScheduler ระบบอัปเดตราคาและข่าวสารอัตโนมัติจะถูกปิดการทำงาน'
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
