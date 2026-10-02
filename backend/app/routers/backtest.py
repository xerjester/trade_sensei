from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

from app.core.limiter import limiter
from app.core.validation import normalize_symbol
from app.services import admin_service, backtest_service

backtest_bp = Blueprint('backtest', __name__, url_prefix='/api/backtest')


@backtest_bp.route('/<symbol>', methods=['POST'])
@jwt_required()
@limiter.limit('10 per minute')
def run_backtest(symbol):
    claims = get_jwt()
    if claims.get('role') not in ('member', 'admin'):
        return jsonify({'status': 'error', 'message': 'สิทธิ์ไม่เพียงพอ'}), 403
    symbol = normalize_symbol(symbol)
    if not symbol:
        return jsonify({'status': 'error', 'message': 'รูปแบบชื่อย่อหุ้นไม่ถูกต้อง'}), 400

    data = request.get_json() or {}
    try:
        months = int(data.get('months', 6))
        initial_amount = float(data.get('initial_amount', 100000))
    except (TypeError, ValueError):
        return jsonify({'status': 'error', 'message': 'รูปแบบเงินลงทุนหรือระยะเวลาไม่ถูกต้อง'}), 400

    try:
        result = backtest_service.run_backtest(symbol, months, initial_amount)
        admin_service.log_system_action(
            action_type='USER_BACKTEST',
            description=(
                f'Backtest {str(symbol).strip().upper()} months={months} amount={initial_amount:.2f}'
            ),
            user_id=int(get_jwt_identity()),
        )
        return jsonify({'status': 'success', 'data': result}), 200
    except ValueError as e:
        admin_service.log_system_action(
            action_type='USER_BACKTEST_FAILED',
            description=f'Backtest failed for {str(symbol).strip().upper()}: {str(e)[:160]}',
            user_id=int(get_jwt_identity()),
        )
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        admin_service.log_system_action(
            action_type='USER_BACKTEST_ERROR',
            description=f'Backtest error for {str(symbol).strip().upper()}: {str(e)[:160]}',
            user_id=int(get_jwt_identity()),
        )
        return jsonify({'status': 'error', 'message': 'ไม่สามารถจำลองผลตอบแทนได้'}), 500
