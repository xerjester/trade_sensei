from app.core.database import db
from app.models import Stock, SystemLog, User
from app.services.stock_service import get_stock_by_symbol


# เพิ่มหุ้นตัวใหม่เข้าสู่ระบบ พร้อมตรวจจับชื่อ/หมวดหมู่อัตโนมัติ ดึงราคา ข่าว และเทรน AI ทันที
def add_stock(symbol: str, company_name: str = '', category: str = '') -> str | None:
    symbol = symbol.strip().upper()
    if get_stock_by_symbol(symbol):
        return f'มีหุ้น {symbol} ในระบบแล้ว'

    import yfinance as yf
    ticker = yf.Ticker(symbol)
    try:
        hist = ticker.history(period='1mo')
        if hist.empty:
            return f'ไม่พบข้อมูลการซื้อขายสำหรับหุ้น {symbol} บน Yahoo Finance กรุณาตรวจสอบตัวย่อ'
    except Exception as e:
        return f'ไม่สามารถเชื่อมต่อข้อมูล Yahoo Finance สำหรับ {symbol} ได้: {str(e)}'

    # ตรวจจับชื่อบริษัทและหมวดหมู่อัตโนมัติจาก Yahoo Finance หากไม่ได้ระบุมา
    info = {}
    try:
        info = ticker.info or {}
    except Exception:
        info = {}

    resolved_name = (company_name or '').strip()
    if not resolved_name:
        resolved_name = info.get('shortName') or info.get('longName') or symbol

    resolved_cat = (category or '').strip()
    if not resolved_cat or resolved_cat.lower() == 'unknown':
        resolved_cat = info.get('sector') or info.get('category') or info.get('industry')
        if not resolved_cat:
            if symbol.endswith('-USD'):
                resolved_cat = 'Crypto'
            elif symbol in ('GLD', 'GOLD'):
                resolved_cat = 'Commodities'
            else:
                resolved_cat = 'Equity'

    stock = Stock(symbol=symbol, company_name=resolved_name, category=resolved_cat)
    db.session.add(stock)
    db.session.commit()

    # ดึงราคา 2 ปี ข่าวสาร และคำนวณโมเดลพยากรณ์ล่วงหน้า 7 วัน
    try:
        from app.services.scraper_service import scrape_news_for_stock
        from app.services.stock_service import fetch_stock_from_yfinance
        from app.services.predictor_service import run_prophet_forecast
        fetch_stock_from_yfinance(symbol)
        scrape_news_for_stock(stock)
        try:
            run_prophet_forecast(stock.stock_id, force_refresh=True)
        except Exception:
            pass
    except Exception:
        pass

    log_system_action(
        'ADMIN_ADD_STOCK',
        f'เพิ่มหุ้น {symbol} ({resolved_name}) หมวดหมู่ {resolved_cat} พร้อมดึงข้อมูลและเตรียมโมเดล AI',
    )
    return None


# ลบหุ้นออกจากระบบ พร้อมข้อมูลราคา ข่าว และโมเดลที่ผูกอยู่
def delete_stock(symbol: str) -> str | None:
    stock = get_stock_by_symbol(symbol)
    if not stock:
        return 'ไม่พบหุ้นที่ต้องการลบ'
    db.session.delete(stock)
    db.session.commit()
    return None


# บันทึกกิจกรรมการทำงานของผู้ใช้หรือระบบลงตาราง system_logs
def log_system_action(action_type: str, description: str, user_id: int | None = None) -> None:
    db.session.add(
        SystemLog(action_type=action_type, description=description, user_id=user_id)
    )
    db.session.commit()


# ดึงประวัติ log การทำงานของระบบมาแสดงบนหน้าจอ Admin
def get_system_logs(
    limit: int = 30,
    user_id: int | None = None,
    action_type: str | None = None,
) -> list[dict]:
    q = (
        db.session.query(SystemLog, User)
        .outerjoin(User, User.user_id == SystemLog.user_id)
        .order_by(SystemLog.created_at.desc())
    )
    if user_id is not None:
        q = q.filter(SystemLog.user_id == user_id)
    if action_type:
        q = q.filter(SystemLog.action_type == action_type)

    rows = q.limit(limit).all()
    data: list[dict] = []
    for log, user in rows:
        data.append(
            {
                'log_id': log.log_id,
                'action_type': log.action_type,
                'description': log.description,
                'created_at': log.created_at.strftime('%Y-%m-%d %H:%M:%S')
                if log.created_at
                else '',
                'user_id': log.user_id,
                'user_email': user.email if user else None,
                'user_role': user.role if user else None,
            }
        )
    return data
