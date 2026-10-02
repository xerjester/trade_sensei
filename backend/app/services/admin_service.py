from app.core.database import db
from app.models import Stock, SystemLog, User
from app.services.stock_service import get_stock_by_symbol


def add_stock(symbol: str, company_name: str, category: str) -> str | None:
    symbol = symbol.strip().upper()
    if get_stock_by_symbol(symbol):
        return 'มีหุ้นตัวนี้ในระบบแล้ว'
    stock = Stock(symbol=symbol, company_name=company_name, category=category)
    db.session.add(stock)
    db.session.commit()

    # หุ้นตัวที่มาทีหลัง ดึงข้อมูลราคาและข่าวสารอัตโนมัติทันที
    try:
        from app.services.scraper_service import scrape_news_for_stock
        from app.services.stock_service import fetch_stock_from_yfinance
        fetch_stock_from_yfinance(symbol)
        scrape_news_for_stock(stock)
    except Exception:
        pass

    return None


def delete_stock(symbol: str) -> str | None:
    stock = get_stock_by_symbol(symbol)
    if not stock:
        return 'ไม่พบหุ้นที่ต้องการลบ'
    db.session.delete(stock)
    db.session.commit()
    return None


def log_system_action(action_type: str, description: str, user_id: int | None = None) -> None:
    db.session.add(
        SystemLog(action_type=action_type, description=description, user_id=user_id)
    )
    db.session.commit()


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
