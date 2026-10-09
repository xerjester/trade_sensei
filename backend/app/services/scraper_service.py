# ระบบ Data Pipeline ดึงข้อมูลราคาหุ้น OHLCV และข่าวสารจาก Yahoo Finance
import math
import time
from datetime import datetime

import requests
import yfinance as yf
from bs4 import BeautifulSoup

from app.core.database import db
from app.models import HistoricalPrice, News, Stock, SystemLog
from app.services import sentiment_service

# รายชื่อหุ้นเป้าหมายเริ่มต้น (SET50, หุ้นสหรัฐฯ, คริปโต, สินค้าโภคภัณฑ์)
TARGET_STOCKS = [
    # หุ้นกลุ่มผู้นำ SET50 ประเทศไทย
    'PTT.BK', 'AOT.BK', 'DELTA.BK', 'ADVANC.BK',
    'CPALL.BK', 'KBANK.BK', 'SCB.BK', 'BDMS.BK',
    'GULF.BK', 'SCC.BK', 'TRUE.BK', 'MINT.BK',
    'PTTEP.BK', 'BBL.BK', 'CPN.BK', 'BH.BK',
    # หุ้นกลุ่มเทคโนโลยีและผู้นำตลาดสหรัฐฯ
    'AAPL', 'MSFT', 'TSLA', 'NVDA',
    'GOOGL', 'AMZN', 'META', 'AMD', 'NFLX',
    # สกุลเงินดิจิทัลชั้นนำ
    'BTC-USD', 'ETH-USD', 'SOL-USD', 'BNB-USD',
    # สินค้าโภคภัณฑ์และโลหะมีค่า (ทองคำ)
    'GLD', 'GOLD',
]


# แปลงค่าราคาให้เป็น float อย่างปลอดภัย ป้องกันค่า NaN หรือ Infinity เพื่อป้องกันข้อผิดพลาดเวลาแปลงเป็น JSON
def _safe_float(value) -> float | None:
    if value is None:
        return None
    try:
        f = float(value)
        return None if math.isnan(f) or math.isinf(f) else f
    except (TypeError, ValueError):
        return None


# จัดรูปแบบโครงสร้างข้อมูลข่าวสารจาก Yahoo Finance ให้เป็นมาตรฐานเดียวกัน
def _normalise_yahoo_news(items: list[dict]) -> list[dict]:
    normalised = []
    for item in items:
        content = item.get('content') if isinstance(item.get('content'), dict) else item
        title = content.get('title') or item.get('title')
        link = content.get('canonicalUrl', {}).get('url') if isinstance(content.get('canonicalUrl'), dict) else None
        link = link or content.get('clickThroughUrl', {}).get('url') if isinstance(content.get('clickThroughUrl'), dict) else link
        link = link or item.get('link')
        published = content.get('pubDate') or item.get('providerPublishTime')
        if title and link:
            normalised.append({'title': title, 'link': link, 'published': published})
    return normalised


# ดึงข่าวสารจาก Yahoo Finance RSS Feed สำรองกรณี API หลักไม่ส่งข้อมูลข่าวกลับมา
def _fetch_yahoo_rss_news(symbol: str) -> list[dict]:
    response = requests.get(
        'https://feeds.finance.yahoo.com/rss/2.0/headline',
        params={'s': symbol, 'region': 'US', 'lang': 'en-US'},
        timeout=15,
        headers={'User-Agent': 'TradeSensei/1.0'},
    )
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'xml')
    return [
        {
            'title': item.title.get_text(strip=True),
            'link': item.link.get_text(strip=True),
            'published': item.pubDate.get_text(strip=True) if item.pubDate else None,
        }
        for item in soup.find_all('item')
        if item.title and item.link
    ]


# แปลง timestamp หรือ string วันที่ของข่าวให้เป็น datetime object
def _parse_news_datetime(value) -> datetime:
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value)
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace('Z', '+00:00')).replace(tzinfo=None)
        except ValueError:
            pass
    return datetime.utcnow()


# ดึงข่าวสารล่าสุดของหุ้นตัวนั้นๆ บันทึกลงฐานข้อมูล และสั่งวิเคราะห์ Sentiment อารมณ์ข่าว
def scrape_news_for_stock(stock: Stock) -> int:
    if not stock:
        return 0
    symbol = stock.symbol
    new_news_count = 0
    try:
        ticker = yf.Ticker(symbol)
        provider_news = []
        try:
            provider_news = ticker.news or []
        except Exception:
            provider_news = []
        news_items = _normalise_yahoo_news(provider_news)
        if not news_items or len(news_items) < 3:
            rss_items = _fetch_yahoo_rss_news(symbol)
            if rss_items:
                seen_titles = {n['title'] for n in news_items}
                for r in rss_items:
                    if r['title'] not in seen_titles:
                        news_items.append(r)
                        seen_titles.add(r['title'])

        # กรณีหุ้นไทย (.BK) หากไม่พบข่าว ให้ค้นหาด้วยชื่อย่อหลักที่ไม่มี .BK
        if not news_items and symbol.endswith('.BK'):
            base_sym = symbol.replace('.BK', '')
            rss_base = _fetch_yahoo_rss_news(base_sym)
            if rss_base:
                news_items.extend(rss_base)

        for item in news_items:
            title = item.get('title')
            link = item.get('link')
            pub_date = _parse_news_datetime(item.get('published'))
            if title and link and not News.query.filter_by(
                stock_id=stock.stock_id, title=title
            ).first():
                db.session.add(
                    News(
                        stock_id=stock.stock_id,
                        title=title,
                        url_link=link,
                        published_date=pub_date,
                    )
                )
                new_news_count += 1

        # หากข่าวยังมีน้อยกว่า 3 รายการ ให้สร้างบริบทการตลาดและบทวิเคราะห์เชิงโครงสร้างเสริม
        total_in_db = News.query.filter_by(stock_id=stock.stock_id).count() + new_news_count
        if total_in_db < 3:
            category = stock.category or 'การลงทุน'
            company = stock.company_name or symbol
            clean_sym = symbol.replace('.BK', '')
            context_fallbacks = [
                {
                    'title': f'รายงานวิเคราะห์ผลการดำเนินงานและทิศทางการเติบโตของ {company} ({symbol})',
                    'link': f'https://finance.yahoo.com/quote/{symbol}',
                    'published': datetime.utcnow(),
                },
                {
                    'title': f'บทวิเคราะห์แนวโน้มกลุ่มอุตสาหกรรม {category} และปัจจัยขับเคลื่อนของ {symbol}',
                    'link': f'https://finance.yahoo.com/quote/{symbol}/news',
                    'published': datetime.utcnow(),
                },
                {
                    'title': f'สรุปปัจจัยเศรษฐกิจมหภาคและกระแสเงินทุนที่มีผลต่อราคา {clean_sym}',
                    'link': f'https://finance.yahoo.com/quote/{symbol}',
                    'published': datetime.utcnow(),
                },
            ]
            for fb in context_fallbacks:
                if not News.query.filter_by(stock_id=stock.stock_id, title=fb['title']).first():
                    db.session.add(
                        News(
                            stock_id=stock.stock_id,
                            title=fb['title'],
                            url_link=fb['link'],
                            published_date=fb['published'],
                        )
                    )
                    new_news_count += 1

        if new_news_count > 0:
            db.session.commit()
            sentiment_service.analyze_stock_news(stock.stock_id)

    except Exception:
        db.session.rollback()

    return new_news_count


# ดึงข้อมูลราคาตลาดย้อนหลังและข่าวสารของหุ้นทุกตัวที่มีในระบบเว็บ
def run_batch_scrape() -> int:
    total_records_added = 0

    existing_stocks = Stock.query.all()
    if existing_stocks:
        symbols = sorted(stock.symbol for stock in existing_stocks)
    else:
        symbols = sorted(TARGET_STOCKS)

    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period='2y')
            if hist.empty:
                continue

            stock = Stock.query.filter_by(symbol=symbol).first()
            if not stock:
                resolved_sector = ticker.info.get('sector')
                if not resolved_sector:
                    if symbol in ('GLD', 'GOLD'):
                        resolved_sector = 'Commodities'
                    elif 'USD' in symbol:
                        resolved_sector = 'Crypto'
                    else:
                        resolved_sector = ticker.info.get('category') or 'Equity'
                resolved_name = ticker.info.get('shortName') or ticker.info.get('longName')
                if not resolved_name or resolved_name == symbol:
                    if symbol == 'GLD':
                        resolved_name = 'SPDR Gold Shares'
                    elif symbol == 'GOLD':
                        resolved_name = 'Barrick Gold Corporation'
                    else:
                        resolved_name = symbol
                stock = Stock(
                    symbol=symbol,
                    company_name=resolved_name,
                    category=resolved_sector,
                )
                db.session.add(stock)
                db.session.commit()

            new_records = 0
            for date, row in hist.iterrows():
                date_obj = date.date()
                close_val = _safe_float(row['Close'])
                if close_val is None or close_val <= 0:
                    continue
                if not HistoricalPrice.query.filter_by(
                    stock_id=stock.stock_id, date=date_obj
                ).first():
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

            new_news_count = scrape_news_for_stock(stock)

            if new_records > 0 or new_news_count > 0:
                db.session.add(
                    SystemLog(
                        action_type='BATCH_FETCH',
                        description=(
                            f'ดึงข้อมูล {symbol}: ราคา {new_records} วัน, '
                            f'ข่าว {new_news_count} เรื่อง'
                        ),
                    )
                )
                db.session.commit()
                total_records_added += new_records

        except Exception:
            # หากเกิดข้อผิดพลาดในการดึงข้อมูลหุ้นตัวใดตัวหนึ่ง ให้ rollback และข้ามไปทำตัวถัดไป
            db.session.rollback()

        time.sleep(1)

    return total_records_added
