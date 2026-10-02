import math
import yfinance as yf

from app.core.database import db
from app.models import HistoricalPrice, News, Stock, SystemLog


def get_stock_by_symbol(symbol: str) -> Stock | None:
    return Stock.query.filter_by(symbol=str(symbol).strip().upper()).first()


def list_all_stocks() -> list[dict]:
    return [
        {
            'symbol': s.symbol,
            'company_name': s.company_name,
            'category': s.category,
        }
        for s in Stock.query.all()
    ]


def _safe_float(value) -> float | None:
    """Convert a price value to float.

    Returns ``None`` for ``NULL`` / ``NaN`` / ``±Inf`` so that Flask's
    ``jsonify`` never emits the JavaScript-only ``NaN`` or ``Infinity``
    literals that ``JSON.parse()`` cannot handle.
    """
    if value is None:
        return None
    try:
        f = float(value)
        return None if math.isnan(f) or math.isinf(f) else f
    except (TypeError, ValueError):
        return None


def get_ohlcv_series(symbol: str) -> dict | None:
    stock = get_stock_by_symbol(symbol)
    if not stock:
        return None
    raw_prices = (
        HistoricalPrice.query.filter_by(stock_id=stock.stock_id)
        .order_by(HistoricalPrice.date.asc())
        .all()
    )
    prices = [
        p for p in raw_prices
        if _safe_float(p.close_price) is not None and _safe_float(p.close_price) > 0
    ]
    return {
        'dates': [p.date.strftime('%Y-%m-%d') for p in prices],
        'opens': [_safe_float(p.open_price) or _safe_float(p.close_price) for p in prices],
        'highs': [_safe_float(p.high_price) or _safe_float(p.close_price) for p in prices],
        'lows': [_safe_float(p.low_price) or _safe_float(p.close_price) for p in prices],
        'closes': [_safe_float(p.close_price) for p in prices],
    }


def get_news_for_symbol(symbol: str, limit: int = 5) -> list[dict] | None:
    stock = get_stock_by_symbol(symbol)
    if not stock:
        return None
    items = (
        News.query.filter_by(stock_id=stock.stock_id)
        .order_by(News.published_date.desc())
        .limit(limit)
        .all()
    )
    # หากหุ้นตัวที่มาทีหลัง หรือหุ้นที่มีข่าวน้อยกว่า 2 เรื่อง ให้ดึงข่าวสดและวิเคราะห์ Sentiment ทันที (ยกเว้นโหมดทดสอบ TESTING)
    from flask import current_app
    is_testing = False
    try:
        is_testing = bool(current_app and current_app.config.get('TESTING'))
    except Exception:
        is_testing = False

    if not is_testing and len(items) < 2:
        try:
            from app.services.scraper_service import scrape_news_for_stock
            added = scrape_news_for_stock(stock)
            if added > 0:
                items = (
                    News.query.filter_by(stock_id=stock.stock_id)
                    .order_by(News.published_date.desc())
                    .limit(limit)
                    .all()
                )
        except Exception:
            pass

    return [
        {
            'title': item.title,
            'link': item.url_link,
            'published_date': (
                item.published_date.strftime('%Y-%m-%d %H:%M')
                if item.published_date
                else 'ล่าสุด'
            ),
        }
        for item in items
    ]


def fetch_stock_from_yfinance(symbol: str) -> tuple[int, str | None]:
    """Pull 2y OHLCV from Yahoo Finance into DB. Returns (new_records, error)."""
    symbol = str(symbol).strip().upper()
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period='2y')

    if hist.empty:
        return 0, f'ไม่พบข้อมูลสำหรับหุ้น {symbol}'

    stock = get_stock_by_symbol(symbol)
    if not stock:
        stock = Stock(
            symbol=symbol,
            company_name=ticker.info.get('shortName', symbol),
            category=ticker.info.get('sector', 'Unknown'),
        )
        db.session.add(stock)
        db.session.commit()

    new_records = 0
    for date, row in hist.iterrows():
        date_obj = date.date()
        close_val = _safe_float(row['Close'])
        if close_val is None or close_val <= 0:
            continue
        exists = HistoricalPrice.query.filter_by(
            stock_id=stock.stock_id, date=date_obj
        ).first()
        if not exists:
            open_val = _safe_float(row['Open']) or close_val
            high_val = _safe_float(row['High']) or close_val
            low_val = _safe_float(row['Low']) or close_val
            vol_val = 0
            try:
                vol_f = float(row['Volume'])
                if not (math.isnan(vol_f) or math.isinf(vol_f)):
                    vol_val = int(vol_f)
            except (TypeError, ValueError):
                vol_val = 0

            db.session.add(
                HistoricalPrice(
                    stock_id=stock.stock_id,
                    date=date_obj,
                    open_price=open_val,
                    high_price=high_val,
                    low_price=low_val,
                    close_price=close_val,
                    volume=vol_val,
                )
            )
            new_records += 1

    db.session.add(
        SystemLog(
            action_type='FETCH_STOCK_DATA',
            description=f'ดึงข้อมูลหุ้น {symbol} จำนวน {new_records} วัน สำเร็จ',
        )
    )
    db.session.commit()
    return new_records, None
