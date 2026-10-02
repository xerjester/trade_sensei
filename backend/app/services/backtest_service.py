"""Time Machine backtest vs deposit benchmark (documents.md §2.2)."""
import math
from datetime import datetime, timedelta

from app.models import HistoricalPrice
from app.services.stock_service import get_stock_by_symbol

DEFAULT_DEPOSIT_RATE_ANNUAL = 0.025  # 2.5% per year


def run_backtest(
    symbol: str,
    months: int = 6,
    initial_amount: float = 100_000,
    deposit_rate_annual: float = DEFAULT_DEPOSIT_RATE_ANNUAL,
) -> dict:
    stock = get_stock_by_symbol(symbol)
    if not stock:
        raise ValueError('ไม่พบข้อมูลหุ้นในระบบ')

    months = max(1, min(months, 24))
    initial_amount = max(1000, float(initial_amount))

    cutoff = datetime.utcnow().date() - timedelta(days=months * 30)
    raw_prices = (
        HistoricalPrice.query.filter_by(stock_id=stock.stock_id)
        .filter(HistoricalPrice.date >= cutoff)
        .order_by(HistoricalPrice.date.asc())
        .all()
    )
    prices = [
        p for p in raw_prices
        if p.close_price is not None and not math.isnan(float(p.close_price)) and float(p.close_price) > 0
    ]

    if len(prices) < 2:
        raise ValueError(
            f'ข้อมูลไม่เพียงพอสำหรับจำลอง {months} เดือน '
            '(ต้องมีอย่างน้อย 2 วันซื้อขาย)'
        )

    start_price = float(prices[0].close_price)
    end_price = float(prices[-1].close_price)
    start_date = prices[0].date
    end_date = prices[-1].date
    days_held = (end_date - start_date).days or 1

    shares = initial_amount / start_price
    final_value = shares * end_price
    stock_profit = final_value - initial_amount
    stock_return_pct = (stock_profit / initial_amount) * 100

    deposit_multiplier = (1 + deposit_rate_annual) ** (days_held / 365)
    deposit_final = initial_amount * deposit_multiplier
    deposit_profit = deposit_final - initial_amount
    deposit_return_pct = (deposit_profit / initial_amount) * 100

    outperforms = stock_return_pct > deposit_return_pct

    return {
        'symbol': stock.symbol,
        'period': {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'days': days_held,
            'months_requested': months,
        },
        'initial_amount': round(initial_amount, 2),
        'stock': {
            'start_price': round(start_price, 4),
            'end_price': round(end_price, 4),
            'final_value': round(final_value, 2),
            'profit': round(stock_profit, 2),
            'return_pct': round(stock_return_pct, 2),
        },
        'deposit_benchmark': {
            'annual_rate_pct': round(deposit_rate_annual * 100, 2),
            'final_value': round(deposit_final, 2),
            'profit': round(deposit_profit, 2),
            'return_pct': round(deposit_return_pct, 2),
        },
        'verdict': (
            f'หุ้น {"ชนะ" if outperforms else "แพ้"}เงินฝาก '
            f'({stock_return_pct:+.2f}% vs {deposit_return_pct:+.2f}%)'
        ),
        'outperforms_deposit': outperforms,
    }
