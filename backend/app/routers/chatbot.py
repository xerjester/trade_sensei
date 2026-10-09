from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

from app.core.limiter import limiter
from app.core.validation import normalize_symbol
from app.services import admin_service, copilot_service

chatbot_bp = Blueprint('chatbot', __name__, url_prefix='/api/copilot')


# API ดึงประวัติการสนทนาระหว่างผู้ใช้งานกับ AI Copilot
@chatbot_bp.route('/history', methods=['GET'])
@jwt_required()
def copilot_history():
    claims = get_jwt()
    if claims.get('role') not in ('member', 'admin'):
        return jsonify({'status': 'error', 'message': 'สิทธิ์ไม่เพียงพอ'}), 403
    try:
        return jsonify({
            'status': 'success',
            'data': copilot_service.get_chat_history(int(get_jwt_identity())),
        }), 200
    except Exception:
        return jsonify({'status': 'error', 'message': 'ไม่สามารถโหลดประวัติการสนทนาได้'}), 500


# API ลบประวัติการสนทนากับ AI Copilot ของผู้ใช้งานปัจจุบัน
@chatbot_bp.route('/history', methods=['DELETE'])
@jwt_required()
def delete_copilot_history():
    claims = get_jwt()
    if claims.get('role') not in ('member', 'admin'):
        return jsonify({'status': 'error', 'message': 'สิทธิ์ไม่เพียงพอ'}), 403
    user_id = int(get_jwt_identity())
    try:
        deleted = copilot_service.clear_chat_history(user_id)
        admin_service.log_system_action(
            action_type='USER_COPILOT_HISTORY_CLEARED',
            description=f'ลบประวัติการสนทนาของ Copilot จำนวน {deleted} รายการ',
            user_id=user_id,
        )
        return jsonify({'status': 'success', 'message': 'ลบประวัติการสนทนาแล้ว', 'deleted': deleted}), 200
    except Exception:
        return jsonify({'status': 'error', 'message': 'ไม่สามารถลบประวัติการสนทนาได้'}), 500


# API ส่งคำถามไปยัง AI Copilot พร้อมระบบ RAG ดึงข้อมูลหุ้นตัวที่ถาม
@chatbot_bp.route('/chat', methods=['POST'])
@jwt_required()
@limiter.limit('20 per minute')
def copilot_chat():
    claims = get_jwt()
    if claims.get('role') not in ('member', 'admin'):
        return jsonify({'status': 'error', 'message': 'สิทธิ์ไม่เพียงพอ'}), 403

    data = request.get_json() or {}
    symbol = normalize_symbol(data.get('symbol'))
    message = str(data.get('message', '')).strip()
    if not symbol:
        return jsonify({'status': 'error', 'message': 'รูปแบบชื่อย่อหุ้นไม่ถูกต้อง'}), 400
    if not message or len(message) > 1000:
        return jsonify({'status': 'error', 'message': 'คำถามต้องมีความยาว 1–1000 ตัวอักษร'}), 400

    try:
        result = copilot_service.chat(int(get_jwt_identity()), symbol, message)
        admin_service.log_system_action(
            action_type='USER_COPILOT_CHAT',
            description=(
                f'สนทนากับ Copilot หุ้น={str(symbol).strip().upper()} ความยาวคำถาม={len(str(message or ""))}'
            ),
            user_id=int(get_jwt_identity()),
        )
        return jsonify({'status': 'success', 'data': result}), 200
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception:
        return jsonify({'status': 'error', 'message': 'Copilot ไม่พร้อมใช้งานในขณะนี้'}), 500
