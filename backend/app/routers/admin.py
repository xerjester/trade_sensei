import os
import subprocess

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity

from app.core.database import db
from app.core.limiter import limiter
from app.core.security import admin_required, user_to_dict
from app.core.validation import normalize_symbol
from app.services import admin_service, predictor_service, user_admin_service

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


@admin_bp.route('/stocks', methods=['POST'])
@admin_required
@limiter.limit('20 per hour')
def add_stock():
    data = request.get_json() or {}
    symbol = normalize_symbol(data.get('symbol'))
    name = data.get('company_name', '')
    cat = (data.get('category') or '').strip()

    if not symbol:
        return jsonify({'status': 'error', 'message': 'กรุณาระบุชื่อย่อหุ้น'}), 400
    if len(str(name)) > 255 or len(str(cat)) > 100:
        return jsonify({'status': 'error', 'message': 'ข้อมูลหุ้นยาวเกินกำหนด'}), 400

    try:
        error = admin_service.add_stock(symbol, name, cat)
        if error:
            return jsonify({'status': 'error', 'message': error}), 400
        return jsonify({
            'status': 'success',
            'message': f'เพิ่มหุ้น {symbol.strip().upper()} สำเร็จ',
        }), 201
    except Exception:
        return jsonify({'status': 'error', 'message': 'ไม่สามารถเพิ่มหุ้นได้'}), 500


@admin_bp.route('/stocks/<symbol>', methods=['DELETE'])
@admin_required
def delete_stock(symbol):
    symbol = normalize_symbol(symbol)
    if not symbol:
        return jsonify({'status': 'error', 'message': 'รูปแบบชื่อย่อหุ้นไม่ถูกต้อง'}), 400
    try:
        error = admin_service.delete_stock(symbol)
        if error:
            return jsonify({'status': 'error', 'message': error}), 404
        return jsonify({
            'status': 'success',
            'message': f'ลบหุ้น {symbol} ออกจากระบบแล้ว',
        }), 200
    except Exception:
        return jsonify({'status': 'error', 'message': 'ไม่สามารถลบหุ้นได้'}), 500


@admin_bp.route('/run-scraper', methods=['POST'])
@admin_required
@limiter.limit('2 per minute')
def run_scraper_api():
    try:
        admin_service.log_system_action(
            action_type='ADMIN_RUN_SCRAPER',
            description='Admin สั่งรัน Scraper (async subprocess)',
            user_id=int(get_jwt_identity()),
        )
        script = os.path.join(
            os.path.dirname(__file__), '..', '..', 'scripts', 'scraper.py'
        )
        subprocess.Popen(['python', script], cwd=os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', '..')
        ))
        return jsonify({
            'status': 'success',
            'message': 'เริ่มระบบดึงข้อมูลแล้ว กรุณารอสักครู่...',
        }), 202
    except Exception:
        return jsonify({'status': 'error', 'message': 'ไม่สามารถเริ่มดึงข้อมูลได้'}), 500


@admin_bp.route('/train-models', methods=['POST'])
@admin_required
@limiter.limit('1 per 5 minutes')
def train_models_api():
    try:
        admin_service.log_system_action(
            action_type='ADMIN_TRAIN_MODELS',
            description='Admin สั่งเทรน Prophet ทุกหุ้น (async subprocess)',
            user_id=int(get_jwt_identity()),
        )
        script = os.path.join(
            os.path.dirname(__file__), '..', '..', 'scripts', 'train_models.py'
        )
        subprocess.Popen(['python', script], cwd=os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', '..')
        ))
        return jsonify({
            'status': 'success',
            'message': 'เริ่มเทรนโมเดล Prophet ทุกหุ้นแล้ว อาจใช้เวลาหลายนาที...',
        }), 202
    except Exception:
        return jsonify({'status': 'error', 'message': 'ไม่สามารถเริ่มเทรนโมเดลได้'}), 500


@admin_bp.route('/train-models/sync', methods=['POST'])
@admin_required
@limiter.limit('1 per 10 minutes')
def train_models_sync():
    """Synchronous batch train (for smaller datasets / testing)."""
    try:
        admin_service.log_system_action(
            action_type='ADMIN_TRAIN_MODELS_SYNC',
            description='Admin สั่งเทรน Prophet ทุกหุ้น (sync)',
            user_id=int(get_jwt_identity()),
        )
        result = predictor_service.run_batch_train_all()
        return jsonify({'status': 'success', 'data': result}), 200
    except Exception:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'ไม่สามารถเทรนโมเดลได้'}), 500


@admin_bp.route('/users', methods=['GET'])
@admin_required
def list_users():
    try:
        users = user_admin_service.list_users()
        return jsonify({'status': 'success', 'data': users}), 200
    except Exception:
        return jsonify({'status': 'error', 'message': 'ไม่สามารถโหลดรายชื่อผู้ใช้ได้'}), 500


@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    data = request.get_json() or {}
    try:
        error = user_admin_service.update_user(
            user_id, data, int(get_jwt_identity())
        )
        if error:
            return jsonify({'status': 'error', 'message': error}), 400
        from app.services.auth_service import get_user_by_id
        user = get_user_by_id(user_id)
        return jsonify({
            'status': 'success',
            'message': 'อัปเดตผู้ใช้สำเร็จ',
            'user': user_to_dict(user),
        }), 200
    except Exception:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'ไม่สามารถอัปเดตผู้ใช้ได้'}), 500


@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    try:
        error = user_admin_service.delete_user(user_id, int(get_jwt_identity()))
        if error:
            return jsonify({'status': 'error', 'message': error}), 400
        return jsonify({
            'status': 'success',
            'message': 'ลบผู้ใช้ออกจากระบบแล้ว',
        }), 200
    except Exception:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'ไม่สามารถลบผู้ใช้ได้'}), 500


@admin_bp.route('/logs', methods=['GET'])
@admin_required
def get_logs():
    limit = request.args.get('limit', 30, type=int)
    filter_user_id = request.args.get('user_id', type=int)
    filter_action_type = request.args.get('action_type', type=str)
    try:
        logs = admin_service.get_system_logs(
            limit=min(limit, 100),
            user_id=filter_user_id,
            action_type=filter_action_type,
        )
        return jsonify({'status': 'success', 'data': logs}), 200
    except Exception:
        return jsonify({'status': 'error', 'message': 'ไม่สามารถโหลดบันทึกระบบได้'}), 500
