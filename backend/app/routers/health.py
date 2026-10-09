from flask import Blueprint, jsonify
from sqlalchemy import text

from app.core.database import db
from app.core.limiter import limiter

health_bp = Blueprint('health', __name__)


# API ตรวจสอบสถานะการทำงานของเซิร์ฟเวอร์ (Health Check)
@health_bp.route('/', methods=['GET'])
@limiter.exempt
def health_check():
    from app.core.config import Config
    return jsonify({
        'status': 'success',
        'message': 'ยินดีต้อนรับสู่ TradeSensei API',
        'cors_origins': list(Config.CORS_ORIGINS),
    }), 200


# API ทดสอบการเชื่อมต่อฐานข้อมูล PostgreSQL
@health_bp.route('/test-db', methods=['GET'])
@limiter.exempt
def test_db():
    try:
        db.session.execute(text('SELECT 1'))
        return jsonify({'status': 'success', 'message': 'Database connected successfully!'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
