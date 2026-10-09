# ระบบวิเคราะห์หุ้นเชิงลึก — รวบรวมแนวโน้มราคาและอารมณ์ข่าวสาร
import math

from app.models import HistoricalPrice, PricePrediction
from app.services import predictor_service, sentiment_service, stock_service


# วิเคราะห์หุ้นเชิงลึก รวบรวมอารมณ์ข่าว (TextBlob) และแนวโน้มราคาจากโมเดล Prophet
def get_deep_analysis(symbol: str) -> dict | None:
    stock = stock_service.get_stock_by_symbol(symbol)
    if not stock:
        return None

    sentiment_service.analyze_stock_news(stock.stock_id)
    sentiment = sentiment_service.get_sentiment_summary(stock.stock_id)

    prices = (
        HistoricalPrice.query.filter_by(stock_id=stock.stock_id)
        .order_by(HistoricalPrice.date.desc())
        .all()
    )
    valid_prices = [
        p for p in prices
        if p.close_price is not None and not math.isnan(float(p.close_price)) and float(p.close_price) > 0
    ][:2]
    latest_price = float(valid_prices[0].close_price) if valid_prices else None
    prev_price = float(valid_prices[1].close_price) if len(valid_prices) > 1 else None
    price_change_pct = None
    if latest_price and prev_price and prev_price != 0:
        price_change_pct = round((latest_price - prev_price) / prev_price * 100, 2)

    predictions = (
        PricePrediction.query.filter_by(stock_id=stock.stock_id)
        .order_by(PricePrediction.predict_date.asc())
        .limit(7)
        .all()
    )

    trend_direction = 'ไม่ทราบ'
    trend_detail = 'ยังไม่มีข้อมูลการทำนาย — กดปุ่ม AI Prediction หรือให้ Admin เทรนโมเดล'
    forecast_change_pct = None

    if predictions:
        first_close = float(predictions[0].predicted_close)
        last_close = float(predictions[-1].predicted_close)
        if latest_price and latest_price != 0 and not math.isnan(latest_price):
            forecast_change_pct = round((last_close - latest_price) / latest_price * 100, 2)
        if last_close > first_close * 1.01:
            trend_direction = 'ขาขึ้น (Uptrend)'
        elif last_close < first_close * 0.99:
            trend_direction = 'ขาลง (Downtrend)'
        else:
            trend_direction = 'ทรงตัว (Sideways)'

        trends = [p.trend_component for p in predictions if p.trend_component]
        if trends:
            try:
                avg_trend = sum(float(t) for t in trends) / len(trends)
                trend_detail = f'องค์ประกอบแนวโน้ม Prophet เฉลี่ย: {avg_trend:.4f}'
            except (ValueError, TypeError):
                trend_detail = 'มีข้อมูลแนวโน้มจาก Prophet แล้ว'

    return {
        'symbol': stock.symbol,
        'company_name': stock.company_name,
        'latest_price': latest_price,
        'price_change_pct': price_change_pct,
        'sentiment': sentiment,
        'trend': {
            'direction': trend_direction,
            'detail': trend_detail,
            'forecast_change_pct': forecast_change_pct,
            'prediction_dates': [p.predict_date.strftime('%Y-%m-%d') for p in predictions],
            'predicted_closes': [float(p.predicted_close) for p in predictions],
        },
        'forecast_quality': predictor_service.get_forecast_quality(stock.stock_id),
    }
