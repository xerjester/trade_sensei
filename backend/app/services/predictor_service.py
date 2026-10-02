"""DFD 3.1 — prepare prices, forecast with Prophet, then store D5 + D7.

The service deliberately uses *only* data available at prediction time.  In
particular, volume is not used as a future regressor because future volume is
unknown and would make the forecast look better in testing than in production.
"""
import json
import logging
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from prophet import Prophet
from prophet.serialize import model_to_json

from app.core.database import db
from app.models import HistoricalPrice, PricePrediction, Stock, StockModel, SystemLog

logging.getLogger('cmdstanpy').setLevel(logging.WARNING)
logging.getLogger('prophet').setLevel(logging.WARNING)

MIN_HISTORY_DAYS = 60
FORECAST_DAYS = 7
CACHE_HOURS = 12
VALIDATION_DAYS = 14


def _predictions_to_dict(rows):
    """Convert persisted D5 rows into the stable API payload."""
    return [
        {
            'predict_date': row.predict_date.strftime('%Y-%m-%d'),
            'predicted_close': float(row.predicted_close),
            'predicted_lower': float(row.predicted_low) if row.predicted_low is not None else None,
            'predicted_upper': float(row.predicted_high) if row.predicted_high is not None else None,
            'trend_component': row.trend_component,
        }
        for row in rows
    ]


def _prepare_price_frame(prices: list[HistoricalPrice]) -> pd.DataFrame:
    """DFD 3.1.1: validate, sort and transform D3 closing prices for Prophet."""
    frame = pd.DataFrame({
        'ds': pd.to_datetime([price.date for price in prices]),
        'close': [float(price.close_price) for price in prices],
    })
    frame = frame.replace([np.inf, -np.inf], np.nan).dropna()
    frame = frame[frame['close'] > 0].drop_duplicates('ds').sort_values('ds')
    if len(frame) < MIN_HISTORY_DAYS:
        raise ValueError(f'ต้องมีราคาที่ใช้ได้อย่างน้อย {MIN_HISTORY_DAYS} วัน')

    # Log scale makes the model respond to percentage moves more consistently
    # across low-priced and high-priced instruments, while expm1 below keeps
    # every published price strictly non-negative.
    frame['y'] = np.log1p(frame.pop('close'))
    return frame[['ds', 'y']]


def _infer_market_frequency(price_frame: pd.DataFrame) -> str:
    """Use calendar days for 24/7 assets; use business days for stock exchanges."""
    weekday_values = price_frame['ds'].dt.weekday
    return 'D' if (weekday_values >= 5).any() else 'B'


def _build_model(history_size: int) -> Prophet:
    """DFD 3.1.2: configure a conservative, repeatable time-series model."""
    return Prophet(
        growth='linear',
        weekly_seasonality=True,
        yearly_seasonality=history_size >= 252,
        daily_seasonality=False,
        seasonality_mode='multiplicative',
        changepoint_prior_scale=0.08,
        seasonality_prior_scale=5.0,
        interval_width=0.90,
        uncertainty_samples=500,
    )


def _validation_metrics(frame: pd.DataFrame, frequency: str) -> dict:
    """Measure a hold-out window so D5 records model quality, not only a guess."""
    holdout = min(VALIDATION_DAYS, max(5, len(frame) // 5))
    if len(frame) < MIN_HISTORY_DAYS + holdout:
        return {'validation_points': 0, 'mae': None, 'mape_pct': None}

    train = frame.iloc[:-holdout]
    actual = np.expm1(frame.iloc[-holdout:]['y'].to_numpy())
    validation_model = _build_model(len(train))
    validation_model.fit(train)
    future = validation_model.make_future_dataframe(periods=holdout, freq=frequency)
    predicted = np.expm1(validation_model.predict(future).tail(holdout)['yhat'].to_numpy())
    absolute_error = np.abs(predicted - actual)
    return {
        'validation_points': int(holdout),
        'mae': round(float(np.mean(absolute_error)), 4),
        'mape_pct': round(float(np.mean(absolute_error / actual) * 100), 2),
    }


def _get_cached_predictions(stock_id, last_price_date):
    cutoff = datetime.utcnow() - timedelta(hours=CACHE_HOURS)
    cached = (
        PricePrediction.query.filter_by(stock_id=stock_id)
        .filter(PricePrediction.created_at >= cutoff)
        .filter(PricePrediction.predict_date > last_price_date)
        .order_by(PricePrediction.predict_date.asc())
        .all()
    )
    return _predictions_to_dict(cached[:FORECAST_DAYS]) if len(cached) >= FORECAST_DAYS else None


def _save_forecast_artifacts(stock_id: int, predictions: list[dict], model: Prophet, metadata: dict) -> None:
    """DFD 3.1.4: atomically persist forecast results and model metadata to D5."""
    PricePrediction.query.filter_by(stock_id=stock_id).delete()
    StockModel.query.filter_by(stock_id=stock_id).delete()
    for item in predictions:
        db.session.add(PricePrediction(
            stock_id=stock_id,
            predict_date=datetime.strptime(item['predict_date'], '%Y-%m-%d').date(),
            predicted_close=item['predicted_close'],
            predicted_low=item['predicted_lower'],
            predicted_high=item['predicted_upper'],
            trend_component=str(item['trend_component']),
        ))

    # JSONB retains the model state, configuration, training date, and hold-out
    # quality metrics.  This meets D5's model-parameter/forecast-components flow.
    db.session.add(StockModel(
        stock_id=stock_id,
        model_json={**metadata, 'prophet_model': json.loads(model_to_json(model))},
    ))
    db.session.commit()


def get_forecast_quality(stock_id: int) -> dict | None:
    """Return safe D5 metadata for the dashboard; never expose the model payload."""
    saved_model = StockModel.query.filter_by(stock_id=stock_id).order_by(StockModel.updated_at.desc()).first()
    if not saved_model or not isinstance(saved_model.model_json, dict):
        return None
    metadata = saved_model.model_json
    validation = metadata.get('validation') or {}
    mape = validation.get('mape_pct')
    # Accuracy is a transparent display metric derived from MAPE, capped to a
    # human-readable 0–100% range; MAE remains the actual price-unit loss.
    accuracy_pct = round(max(0, min(100, 100 - float(mape))), 2) if mape is not None else None
    return {
        'trained_at': metadata.get('trained_at'),
        'training_rows': metadata.get('training_rows'),
        'validation': {**validation, 'accuracy_pct': accuracy_pct},
    }


def run_prophet_forecast(stock_id: int, force_refresh: bool = False) -> tuple[list[dict], bool]:
    """DFD 3.1.1–3.1.4: prepare D3 prices, predict seven market days, store D5."""
    prices = HistoricalPrice.query.filter_by(stock_id=stock_id).order_by(HistoricalPrice.date.asc()).all()
    if len(prices) < MIN_HISTORY_DAYS:
        raise ValueError(
            f'ต้องมีข้อมูลราคาอย่างน้อย {MIN_HISTORY_DAYS} วัน (ปัจจุบันมี {len(prices)} วัน) '
            'กรุณาให้ Admin รัน Scraper หรือดึงข้อมูลหุ้นก่อน'
        )

    last_price_date = prices[-1].date
    if not force_refresh:
        cached = _get_cached_predictions(stock_id, last_price_date)
        if cached:
            return cached, True

    frame = _prepare_price_frame(prices)
    frequency = _infer_market_frequency(frame)
    metrics = _validation_metrics(frame, frequency)
    model = _build_model(len(frame))
    model.fit(frame)

    # freq is inferred from stored D3 data, avoiding weekday-only forecasts for crypto.
    future = model.make_future_dataframe(periods=FORECAST_DAYS, freq=frequency)
    forecast = model.predict(future)
    future_only = forecast[forecast['ds'] > frame['ds'].max()].head(FORECAST_DAYS)
    if len(future_only) != FORECAST_DAYS:
        raise ValueError('โมเดลไม่สามารถสร้างการทำนายได้ครบ 7 วัน')

    predictions = []
    for _, row in future_only.iterrows():
        predictions.append({
            'predict_date': row['ds'].strftime('%Y-%m-%d'),
            'predicted_close': round(float(max(0, np.expm1(row['yhat']))), 4),
            'predicted_lower': round(float(max(0, np.expm1(row['yhat_lower']))), 4),
            'predicted_upper': round(float(max(0, np.expm1(row['yhat_upper']))), 4),
            'trend_component': round(float(max(0, np.expm1(row['trend']))), 4),
        })

    _save_forecast_artifacts(stock_id, predictions, model, {
        'model_name': 'Prophet',
        'forecast_days': FORECAST_DAYS,
        'frequency': frequency,
        'trained_at': datetime.utcnow().isoformat(),
        'training_rows': int(len(frame)),
        'validation': metrics,
    })
    return predictions, False


def run_batch_train_all() -> dict:
    """Admin DFD 3.1 trigger: train every stock and record the D7 audit event."""
    success, failed = [], []
    for stock in Stock.query.all():
        try:
            run_prophet_forecast(stock.stock_id, force_refresh=True)
            success.append(stock.symbol)
        except Exception as exc:
            db.session.rollback()
            failed.append({'symbol': stock.symbol, 'error': str(exc)})

    db.session.add(SystemLog(
        action_type='TRAIN_MODELS',
        description=f'Batch train เสร็จ: สำเร็จ {len(success)} ตัว, ล้มเหลว {len(failed)} ตัว',
    ))
    db.session.commit()
    return {'trained': success, 'failed': failed, 'success_count': len(success), 'failed_count': len(failed)}
