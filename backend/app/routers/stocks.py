from flask import Blueprint, jsonify, request

from app.core.database import db
from app.core.limiter import limiter
from app.core.security import admin_required
from app.core.validation import normalize_symbol
from app.services import stock_service

stocks_bp = Blueprint('stocks', __name__, url_prefix='/api')


@stocks_bp.route('/stocks', methods=['GET'])
@limiter.exempt
def get_all_stocks():
    try:
        return jsonify({'status': 'success', 'data': stock_service.list_all_stocks()}), 200
    except Exception:
        return jsonify({'status': 'error', 'message': 'ไม่สามารถโหลดรายชื่อหุ้นได้'}), 500


@stocks_bp.route('/stock-data/<symbol>', methods=['GET'])
@limiter.exempt
def get_stock_data(symbol):
    if not normalize_symbol(symbol):
        return jsonify({'status': 'error', 'message': 'รูปแบบชื่อย่อหุ้นไม่ถูกต้อง'}), 400
    data = stock_service.get_ohlcv_series(symbol)
    if data is None:
        return jsonify({'status': 'error', 'message': 'ไม่พบข้อมูลหุ้นในระบบ'}), 404
    return jsonify({'status': 'success', 'data': data}), 200


@stocks_bp.route('/fetch-stock', methods=['POST'])
@admin_required
def fetch_stock_data():
    data = request.get_json() or {}
    symbol = normalize_symbol(data.get('symbol'))
    if not symbol:
        return jsonify({'status': 'error', 'message': 'กรุณาระบุชื่อหุ้น (symbol)'}), 400

    try:
        new_records, error = stock_service.fetch_stock_from_yfinance(symbol)
        if error:
            return jsonify({'status': 'error', 'message': error}), 404
        return jsonify({
            'status': 'success',
            'message': f'ดึงข้อมูลและบันทึกหุ้น {str(symbol).strip().upper()} สำเร็จ!',
            'new_records_added': new_records,
        }), 200
    except Exception:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'ไม่สามารถดึงข้อมูลหุ้นได้'}), 500
