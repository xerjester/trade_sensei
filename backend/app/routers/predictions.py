from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

from app.core.database import db
from app.core.limiter import limiter
from app.services import admin_service, predictor_service, stock_service

predictions_bp = Blueprint('predictions', __name__, url_prefix='/api')


# API พยากรณ์ราคาหุ้นล่วงหน้า 30 วันด้วยโมเดล Facebook Prophet
@predictions_bp.route('/predict/<symbol>', methods=['GET'])
@limiter.limit('60 per minute')
@jwt_required()
def get_stock_prediction(symbol):
    claims = get_jwt()
    if claims.get('role') not in ('member', 'admin'):
        return jsonify({'status': 'error', 'message': 'สิทธิ์ไม่เพียงพอ'}), 403

    stock = stock_service.get_stock_by_symbol(symbol)
    if not stock:
        return jsonify({'status': 'error', 'message': 'ไม่พบข้อมูลหุ้นในระบบ'}), 404

    try:
        predictions, from_cache = predictor_service.run_prophet_forecast(stock.stock_id)
        admin_service.log_system_action(
            action_type='USER_PREDICT',
            description=f'Predict {stock.symbol} (cached={from_cache})',
            user_id=int(get_jwt_identity()),
        )
        return jsonify({
            'status': 'success',
            'cached': from_cache,
            'model': 'Facebook Prophet',
            'quality': predictor_service.get_forecast_quality(stock.stock_id),
            'data': {
                'dates': [p['predict_date'] for p in predictions],
                'closes': [p['predicted_close'] for p in predictions],
                'lowers': [p['predicted_lower'] for p in predictions],
                'uppers': [p['predicted_upper'] for p in predictions],
            },
        }), 200
    except ValueError as e:
        admin_service.log_system_action(
            action_type='USER_PREDICT_FAILED',
            description=f'Predict failed for {stock.symbol}: {str(e)[:160]}',
            user_id=int(get_jwt_identity()),
        )
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        admin_service.log_system_action(
            action_type='USER_PREDICT_ERROR',
            description=f'Predict error for {stock.symbol}: {str(e)[:160]}',
            user_id=int(get_jwt_identity()),
        )
        return jsonify({'status': 'error', 'message': 'การทำนายล้มเหลว กรุณาลองใหม่อีกครั้ง'}), 500
