from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

from app.core.limiter import limiter
from app.core.validation import normalize_symbol
from app.services import admin_service, analysis_service

analysis_bp = Blueprint('analysis', __name__, url_prefix='/api')


@analysis_bp.route('/analysis/<symbol>', methods=['GET'])
@limiter.exempt
@jwt_required()
def get_analysis(symbol):
    claims = get_jwt()
    if claims.get('role') not in ('member', 'admin'):
        return jsonify({'status': 'error', 'message': 'สิทธิ์ไม่เพียงพอ'}), 403
    symbol = normalize_symbol(symbol)
    if not symbol:
        return jsonify({'status': 'error', 'message': 'รูปแบบชื่อย่อหุ้นไม่ถูกต้อง'}), 400

    try:
        data = analysis_service.get_deep_analysis(symbol)
    except Exception:
        return jsonify({'status': 'error', 'message': 'ไม่สามารถวิเคราะห์ข้อมูลได้'}), 500
    if not data:
        admin_service.log_system_action(
            action_type='USER_ANALYSIS_NOT_FOUND',
            description=f'Analysis not found for {str(symbol).strip().upper()}',
            user_id=int(get_jwt_identity()),
        )
        return jsonify({'status': 'error', 'message': 'ไม่พบข้อมูลหุ้นในระบบ'}), 404

    admin_service.log_system_action(
        action_type='USER_ANALYSIS',
        description=f'Get analysis for {str(symbol).strip().upper()}',
        user_id=int(get_jwt_identity()),
    )
    return jsonify({'status': 'success', 'data': data}), 200
