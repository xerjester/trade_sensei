# สคริปต์เพิ่มข้อมูลหุ้นและประวัติราคาจำลองเริ่มต้นในฐานข้อมูล
import math
import random
from datetime import datetime, timedelta
import yfinance as yf
from app import create_app
from app.core.database import db
from app.models import Stock, HistoricalPrice, News, NewsSentiment
from app.services.scraper_service import TARGET_STOCKS, _safe_float

STOCK_METADATA = {
    'CPALL.BK': ('CP ALL Public Company Limited', 'Consumer Staples', 56.50),
    'KBANK.BK': ('Kasikornbank Public Company Limited', 'Financial Services', 155.00),
    'SCB.BK': ('SCB X Public Company Limited', 'Financial Services', 112.50),
    'BDMS.BK': ('Bangkok Dusit Medical Services', 'Healthcare', 28.00),
    'GULF.BK': ('Gulf Energy Development', 'Utilities', 63.50),
    'SCC.BK': ('Siam Cement Public Company Limited', 'Basic Materials', 198.00),
    'TRUE.BK': ('True Corporation', 'Communication Services', 11.80),
    'MINT.BK': ('Minor International', 'Consumer Cyclical', 29.50),
    'PTTEP.BK': ('PTT Exploration and Production', 'Energy', 134.00),
    'BBL.BK': ('Bangkok Bank Public Company Limited', 'Financial Services', 152.00),
    'CPN.BK': ('Central Pattana Public Company Limited', 'Real Estate', 65.00),
    'BH.BK': ('Bumrungrad Hospital Public Company Limited', 'Healthcare', 268.00),
    'GOOGL': ('Alphabet Inc.', 'Communication Services', 165.20),
    'AMZN': ('Amazon.com Inc.', 'Consumer Cyclical', 188.50),
    'META': ('Meta Platforms Inc.', 'Communication Services', 560.00),
    'AMD': ('Advanced Micro Devices Inc.', 'Technology', 158.00),
    'NFLX': ('Netflix Inc.', 'Communication Services', 705.00),
    'SOL-USD': ('Solana USD', 'Crypto', 148.50),
    'BNB-USD': ('BNB USD', 'Crypto', 585.00),
    'GLD': ('SPDR Gold Shares (กองทุนทองคำแท่ง)', 'Commodities', 392.50),
    'GOLD': ('Barrick Gold Corporation (เหมืองทองคำ)', 'Commodities', 43.70),
}

app = create_app()
with app.app_context():
    print(f"Total target stocks to ensure: {len(TARGET_STOCKS)}")
    added_stocks = 0
    today = datetime.utcnow().date()

    for symbol in TARGET_STOCKS:
        stock = Stock.query.filter_by(symbol=symbol).first()
        if not stock:
            name, cat, base_price = STOCK_METADATA.get(symbol, (symbol, 'Equity', 50.0))
            stock = Stock(symbol=symbol, company_name=name, category=cat)
            db.session.add(stock)
            db.session.commit()
            added_stocks += 1
            print(f"Created new stock: {symbol} - {name} ({cat})")

        # ตรวจสอบประวัติราคาที่มีอยู่แล้วในฐานข้อมูล
        hp_count = HistoricalPrice.query.filter_by(stock_id=stock.stock_id).count()
        if hp_count < 30:
            print(f"Fetching/generating price series for {symbol} (currently {hp_count} records)...")
            fetched = False
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period='1y')
                if not hist.empty:
                    for date, row in hist.iterrows():
                        d_obj = date.date()
                        close_val = _safe_float(row['Close'])
                        if close_val is None or close_val <= 0:
                            continue
                        if not HistoricalPrice.query.filter_by(stock_id=stock.stock_id, date=d_obj).first():
                            db.session.add(HistoricalPrice(
                                stock_id=stock.stock_id,
                                date=d_obj,
                                open_price=_safe_float(row['Open']) or close_val,
                                high_price=_safe_float(row['High']) or close_val,
                                low_price=_safe_float(row['Low']) or close_val,
                                close_price=close_val,
                                volume=int(row['Volume']) if not math.isnan(row['Volume']) else 1000000,
                            ))
                    db.session.commit()
                    fetched = True
                    print(f"  Successfully fetched yfinance data for {symbol}")
            except Exception as e:
                print(f"  yfinance fetch skipped for {symbol}: {e}")

            if not fetched:
                # จำลองข้อมูลราคาย้อนหลัง 1 ปีอย่างสมจริง กรณีดึงจาก yfinance ไม่ได้
                name, cat, base_price = STOCK_METADATA.get(symbol, (symbol, 'Equity', 50.0))
                price = base_price * 0.85
                random.seed(sum(ord(c) for c in symbol))
                for day_offset in range(260, 0, -1):
                    d = today - timedelta(days=int(day_offset * 1.4))
                    if d.weekday() >= 5:  # skip weekends
                        continue
                    pct_change = random.uniform(-0.025, 0.028)
                    price = max(1.0, round(price * (1 + pct_change), 2))
                    high = round(price * (1 + random.uniform(0.005, 0.02)), 2)
                    low = round(price * (1 - random.uniform(0.005, 0.02)), 2)
                    op = round(low + (high - low) * random.random(), 2)
                    vol = random.randint(500_000, 15_000_000)

                    if not HistoricalPrice.query.filter_by(stock_id=stock.stock_id, date=d).first():
                        db.session.add(HistoricalPrice(
                            stock_id=stock.stock_id,
                            date=d,
                            open_price=op,
                            high_price=high,
                            low_price=low,
                            close_price=price,
                            volume=vol,
                        ))
                db.session.commit()
                print(f"  Generated synthesized price history for {symbol}")

        # ตรวจสอบและสร้างข่าวเริ่มต้นของหุ้น
        news_count = News.query.filter_by(stock_id=stock.stock_id).count()
        if news_count == 0:
            n = News(
                stock_id=stock.stock_id,
                title=f"รายงานสรุปแนวโน้มผลการดำเนินงานและทิศทางธุรกิจ {symbol}",
                url_link=f"https://www.set.or.th/th/market/product/stock/quote/{symbol.replace('.BK', '')}",
                published_date=datetime.utcnow() - timedelta(hours=random.randint(1, 48)),
            )
            db.session.add(n)
            db.session.flush()
            db.session.add(NewsSentiment(
                news_id=n.news_id,
                sentiment_score=0.25,
                sentiment_label='Positive',
                reason_text='แนวโน้มผลประกอบการและปัจจัยพื้นฐานอยู่ในเกณฑ์แข็งแกร่ง'
            ))
            db.session.commit()

    total_stocks = Stock.query.count()
    print(f"\nAll done! Total stocks in database: {total_stocks}")
