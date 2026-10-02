"""Sensei Copilot — strict, database-grounded answers with human-friendly communication (documents.md §4.2)."""
from __future__ import annotations

import json
import logging
import math

from app.core.config import Config
from app.core.database import db
from app.models import ChatHistory, HistoricalPrice, PricePrediction
from app.services import (
    analysis_service,
    backtest_service,
    predictor_service,
    sentiment_service,
    stock_service,
)
from app.services.copilot_rules import (
    GEMINI_COPILOT_SYSTEM_INSTRUCTION,
    compose_human_grounded_response,
)

PROVIDER = 'AI_Copilot'
logger = logging.getLogger(__name__)


def _get_gemini_rewriter():
    """Create the optional language-only Gemini client; facts stay local to TradeSensei Big Knowledge."""
    if not Config.GEMINI_API_KEY:
        return None
    try:
        import google.generativeai as genai
        genai.configure(api_key=Config.GEMINI_API_KEY)
        return genai.GenerativeModel(Config.GEMINI_MODEL)
    except Exception:
        return None


def get_chat_history(user_id: int, limit: int = 30) -> list[dict]:
    """DFD 5.1: retrieve only the requesting member's D6 conversation records."""
    rows = (
        ChatHistory.query.filter_by(user_id=user_id)
        .order_by(ChatHistory.times.desc(), ChatHistory.chat_id.desc())
        .limit(max(1, min(limit, 50)))
        .all()
    )
    # The query is newest-first for efficiency; reverse it for natural reading.
    return [
        {
            'message': row.message,
            'response': row.response_text or '',
            'provider': row.provider,
            'sent_at': row.times.strftime('%Y-%m-%d %H:%M') if row.times else '',
        }
        for row in reversed(rows)
    ]


def clear_chat_history(user_id: int) -> int:
    """DFD 5.5: delete only the requesting member's stored D6 records."""
    deleted = ChatHistory.query.filter_by(user_id=user_id).delete(synchronize_session=False)
    db.session.commit()
    return deleted


def build_rag_components(symbol: str, user_id: int) -> dict:
    """Build the complete structured Big Knowledge data and factual lines for a stock."""
    stock = stock_service.get_stock_by_symbol(symbol)
    if not stock:
        return {
            'stock': None,
            'raw_lines': [f'ไม่พบข้อมูลหุ้น {symbol}'],
            'latest_price': None,
            'technical': None,
            'prophet': None,
            'sentiment': None,
            'backtest': None,
        }

    lines = [
        f'[D2] สินทรัพย์: {stock.symbol} ({stock.company_name})',
        f'[D2] หมวดหมู่: {stock.category or "N/A"}',
    ]

    latest_price_info = None
    technical_info = None

    # 1. Historical Prices & Technical Indicators (D3)
    prices = (
        HistoricalPrice.query.filter_by(stock_id=stock.stock_id)
        .order_by(HistoricalPrice.date.desc())
        .all()
    )
    valid_prices = [
        p for p in prices
        if p.close_price is not None and not math.isnan(float(p.close_price)) and float(p.close_price) > 0
    ]

    if valid_prices:
        latest = valid_prices[0]
        latest_close = float(latest.close_price)
        latest_date_str = latest.date.strftime('%Y-%m-%d') if hasattr(latest.date, 'strftime') else str(latest.date)

        chg_amt = 0.0
        chg_pct = 0.0
        if len(valid_prices) > 1:
            prev_close = float(valid_prices[1].close_price)
            chg_amt = round(latest_close - prev_close, 2)
            chg_pct = round((latest_close - prev_close) / prev_close * 100, 2) if prev_close > 0 else 0.0
            lines.append(
                f'[D3] ราคาปิดล่าสุด ({latest_date_str}): {latest_close:.2f} บาท | เปลี่ยนแปลง: {chg_amt:+.2f} บาท ({chg_pct:+.2f}%)'
            )
        else:
            lines.append(f'[D3] ราคาปิดล่าสุด ({latest_date_str}): {latest_close:.2f} บาท')

        latest_price_info = {
            'price': latest_close,
            'date': latest_date_str,
            'change_val': chg_amt,
            'change_pct': chg_pct,
        }

        # 1-Year (up to 264 trading days) High / Low & SMA
        recent_1y = valid_prices[:264]
        highs = [float(p.high_price) for p in recent_1y if p.high_price is not None and not math.isnan(float(p.high_price))]
        lows = [float(p.low_price) for p in recent_1y if p.low_price is not None and not math.isnan(float(p.low_price))]
        high_val = max(highs) if highs else latest_close
        low_val = min(lows) if lows else latest_close

        tech_parts = [f'ราคาสูงสุดรอบ 1 ปี: {high_val:.2f} บาท', f'ราคาต่ำสุดรอบ 1 ปี: {low_val:.2f} บาท']
        sma20_val = None
        sma50_val = None
        if len(valid_prices) >= 20:
            sma20_val = round(sum(float(p.close_price) for p in valid_prices[:20]) / 20, 2)
            tech_parts.append(f'SMA 20: {sma20_val:.2f} บาท')
        if len(valid_prices) >= 50:
            sma50_val = round(sum(float(p.close_price) for p in valid_prices[:50]) / 50, 2)
            tech_parts.append(f'SMA 50: {sma50_val:.2f} บาท')

        lines.append(f'[D3] สัญญาณและกรอบราคาเทคนิคอล: {" | ".join(tech_parts)}')

        technical_info = {
            'high_1y': high_val,
            'low_1y': low_val,
            'sma20': sma20_val,
            'sma50': sma50_val,
        }

    # 2. Deep Analysis & AI Prophet Forecast (D5)
    prophet_info = None
    try:
        deep = analysis_service.get_deep_analysis(stock.symbol)
    except Exception:
        deep = None

    if deep and deep.get('trend'):
        trend = deep['trend']
        t_dir = trend.get('direction', 'ไม่ทราบ')
        f_pct = trend.get('forecast_change_pct')
        f_pct_str = f'{f_pct:+.2f}%' if f_pct is not None else 'N/A'
        dates = trend.get('prediction_dates') or []
        closes = trend.get('predicted_closes') or []
        forecast_str = ', '.join(f'{d}: {c:.2f}' for d, c in zip(dates, closes)) if dates and closes else 'N/A'
        lines.append(f'[D5] การพยากรณ์ AI Prophet (7 วัน): ทิศทาง {t_dir} | คาดการณ์เปลี่ยนแปลง {f_pct_str}')
        if forecast_str != 'N/A':
            lines.append(f'[D5] ราคาคาดการณ์ 7 วันข้างหน้า: {forecast_str}')
        if trend.get('detail'):
            lines.append(f'[D5] รายละเอียดแนวโน้ม: {trend["detail"]}')

        val = (deep.get('forecast_quality') or {}).get('validation') or {}
        prophet_info = {
            'direction': t_dir,
            'forecast_change_pct': f_pct or 0.0,
            'accuracy_pct': val.get('accuracy_pct'),
            'mae': val.get('mae'),
            'predicted_dates': dates,
            'predicted_closes': closes,
        }

    if deep and deep.get('forecast_quality'):
        val = deep['forecast_quality'].get('validation') or {}
        if val.get('validation_points'):
            lines.append(
                f'[D5] ความน่าเชื่อถือของโมเดล AI: Accuracy {val.get("accuracy_pct", "N/A")}% | Loss (MAE) {val.get("mae", "N/A")} | ทดสอบย้อนหลัง {val.get("validation_points")} วัน'
            )

    # 3. Market Sentiment & News (D4)
    sentiment = deep.get('sentiment') if deep else None
    if not sentiment:
        try:
            sentiment_service.analyze_stock_news(stock.stock_id)
            sentiment = sentiment_service.get_sentiment_summary(stock.stock_id)
        except Exception:
            sentiment = None

    sentiment_info = None
    if sentiment:
        lines.append(
            f'[D4] อารมณ์ข่าวเฉลี่ย: {sentiment["average_score"]:+.2f} ({sentiment["overall_label"]}) '
            f'[+{sentiment["positive_count"]} / -{sentiment["negative_count"]} / ={sentiment["neutral_count"]}]'
        )
        sample_titles = []
        for item in sentiment.get('items', [])[:4]:
            t = item.get('title', '')[:90]
            if t:
                sample_titles.append(t)
            lines.append(f'[D4] ข่าว [{item.get("label", "Neutral")}]: {t}')

        sentiment_info = {
            'average_score': sentiment.get('average_score', 0.0),
            'overall_label': sentiment.get('overall_label', 'Neutral'),
            'positive_count': sentiment.get('positive_count', 0),
            'negative_count': sentiment.get('negative_count', 0),
            'neutral_count': sentiment.get('neutral_count', 0),
            'sample_titles': sample_titles,
        }

    # 4. Time Machine / Backtest Simulation (D7)
    backtest_info = None
    try:
        backtest = backtest_service.run_backtest(stock.symbol, initial_amount=100000.0, months=6)
        if backtest and 'stock' in backtest and 'deposit_benchmark' in backtest:
            stk_ret = backtest['stock'].get('return_pct', 0.0)
            stk_prof = backtest['stock'].get('profit', 0.0)
            dep_ret = backtest['deposit_benchmark'].get('return_pct', 0.0)
            verdict = backtest.get('verdict', '')
            lines.append(
                f'[D7] การจำลองผลตอบแทน Time Machine (ย้อนหลัง 6 เดือน): หุ้น {stk_ret:+.2f}% (กำไร/ขาดทุน {stk_prof:+,.2f} บาท) เทียบเงินฝาก 2.5%/ปี ({dep_ret:+.2f}%) | ข้อสรุป: {verdict}'
            )
            backtest_info = {
                'stock_return_pct': stk_ret,
                'profit': stk_prof,
                'deposit_return_pct': dep_ret,
                'verdict': verdict,
            }
    except Exception as e:
        logger.debug('Backtest summary in copilot context failed: %s', e)

    return {
        'stock': stock,
        'raw_lines': lines,
        'latest_price': latest_price_info,
        'technical': technical_info,
        'prophet': prophet_info,
        'sentiment': sentiment_info,
        'backtest': backtest_info,
    }


def build_rag_context(symbol: str, user_id: int) -> str:
    """Build the complete factual Big Knowledge boundary string for an answer from TradeSensei data only."""
    components = build_rag_components(symbol, user_id)
    return '\n'.join(components['raw_lines'])


def _grounded_response(
    context: str,
    message: str,
    symbol: str,
    components: dict | None = None,
) -> tuple[str, list[str]]:
    """Produce a human-friendly, empathetic, conversational response grounded strictly in TradeSensei facts."""
    if not components or not components.get('stock'):
        components = build_rag_components(symbol, 0)

    stock = components.get('stock')
    if not stock:
        return f'ขออภัยครับ ผมยังไม่พบข้อมูลหุ้น {symbol} ในระบบ TradeSensei ในขณะนี้ครับ', []

    answer, flags = compose_human_grounded_response(
        symbol=stock.symbol,
        company_name=stock.company_name,
        category=stock.category or 'หุ้นทั่วไป',
        latest_price_info=components.get('latest_price'),
        technical_info=components.get('technical'),
        prophet_info=components.get('prophet'),
        sentiment_info=components.get('sentiment'),
        backtest_info=components.get('backtest'),
        user_query=message,
    )

    if 'NO_DISCLAIMER' in (flags or []):
        return answer, flags

    full_answer = (
        f"{answer}\n\n"
        "หมายเหตุ: ข้อมูลทั้งหมดรวบรวมจากระบบ TradeSensei เพื่อการศึกษาและประกอบการวิเคราะห์เท่านั้น ไม่ใช่คำแนะนำในการลงทุน"
    )
    return full_answer, flags


def _rewrite_with_gemini(facts: str, question: str, symbol: str) -> str | None:
    """Use Gemini with Sensei Persona & Rules to craft human-friendly Thai explanations strictly grounded in facts."""
    model = _get_gemini_rewriter()
    if not model:
        return None

    prompt = f"""{GEMINI_COPILOT_SYSTEM_INSTRUCTION}

คำถามของผู้ใช้: {question}

BIG KNOWLEDGE ({symbol}):
{facts}
"""
    try:
        result = model.generate_content(
            prompt,
            generation_config={
                'temperature': 0.15,
                'response_mime_type': 'application/json',
            },
        )
        raw_response = result.text.strip()
        if raw_response.startswith('```'):
            raw_response = raw_response.split('\n', 1)[-1].rsplit('```', 1)[0].strip()
        payload = json.loads(raw_response)
        answer = str(payload.get('answer') or '').strip()
        if not answer:
            return None

        # Clean any accidental citation references to guarantee strict compliance
        import re
        answer = re.sub(r'\[D[1-9]\]', '', answer)
        answer = re.sub(r'แหล่งอ้างอิง:.*', '', answer, flags=re.MULTILINE).strip()

        return (
            f"{answer}\n\n"
            "หมายเหตุ: ข้อมูลทั้งหมดรวบรวมจากระบบ TradeSensei เพื่อการศึกษาและประกอบการวิเคราะห์เท่านั้น ไม่ใช่คำแนะนำในการลงทุน"
        )
    except Exception as error:
        logger.warning('Gemini grounded rewrite failed: %s', error)
        return None


def chat(user_id: int, symbol: str, message: str) -> dict:
    message = (message or '').strip()
    if not message:
        raise ValueError('กรุณาพิมพ์คำถาม')

    symbol = str(symbol).strip().upper()
    components = build_rag_components(symbol, user_id)
    context = '\n'.join(components['raw_lines'])

    # Deterministic response is always computed as the core grounded rule engine
    deterministic_response, flags = _grounded_response(context, message, symbol, components)

    # For chit-chat, identity, and out-of-domain rejections, return immediately without LLM rewrite
    if 'NO_DISCLAIMER' in (flags or []):
        response_text = deterministic_response
        provider_name = f'{PROVIDER}_Grounded'
    else:
        rewritten_response = _rewrite_with_gemini(context, message, symbol)
        if rewritten_response:
            response_text = rewritten_response
            provider_name = f'{PROVIDER}_Gemini_Grounded'
        else:
            response_text = deterministic_response
            provider_name = f'{PROVIDER}_Grounded'

    record = ChatHistory(
        user_id=user_id,
        message=message,
        response_text=response_text,
        provider=PROVIDER,
    )
    db.session.add(record)
    db.session.commit()

    return {
        'response': response_text,
        'provider': provider_name,
        'symbol': symbol,
    }
