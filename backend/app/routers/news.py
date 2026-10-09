from flask import Blueprint, jsonify

from app.core.limiter import limiter
from app.core.validation import normalize_symbol
from app.services import stock_service

news_bp = Blueprint('news', __name__, url_prefix='/api')


# API ดึงรายการข่าวสารล่าสุดของหุ้นตัวนั้นๆ พร้อมบทวิเคราะห์อารมณ์ข่าว
@news_bp.route('/news/<symbol>', methods=['GET'])
@limiter.exempt
def get_stock_news(symbol):
    if not normalize_symbol(symbol):
        return jsonify({'status': 'error', 'message': 'รูปแบบชื่อย่อหุ้นไม่ถูกต้อง'}), 400
    try:
        items = stock_service.get_news_for_symbol(symbol)
        if items is None:
            return jsonify({'status': 'error', 'message': 'ไม่พบข้อมูลหุ้นในระบบ'}), 404
        return jsonify({'status': 'success', 'data': items}), 200
    except Exception:
        return jsonify({'status': 'error', 'message': 'ไม่สามารถโหลดข่าวได้'}), 500
