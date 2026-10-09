from flask import Blueprint, request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

from app.core.config import Config
from app.core.http import error_response, success_response
from app.core.limiter import limiter
from app.core.security import user_to_dict
from app.core.validation import normalize_email, normalize_person_name, password_error
from app.services import admin_service, auth_service, google_auth_service

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


# ตรวจสอบว่า Google Client ID ได้รับการตั้งค่าอย่างถูกต้องและไม่ใช่ค่า placeholder
def _is_configured_client_id(cid: str) -> bool:
    if not cid:
        return False
    lower = cid.strip().lower()
    return not any(p in lower for p in ('your_google', 'your_', 'placeholder', 'example', 'change_me'))


# API ดึงการตั้งค่า Authentication สำหรับ Frontend (เช่น Google Client ID)
@auth_bp.route('/config', methods=['GET'])
def auth_config():
    valid_id = Config.GOOGLE_CLIENT_ID if _is_configured_client_id(Config.GOOGLE_CLIENT_ID) else None
    return success_response(
        data={
            'google_client_id': valid_id,
            'google_login_enabled': bool(valid_id),
        }
    )


# API เข้าสู่ระบบด้วยอีเมลและรหัสผ่าน
@auth_bp.route('/login', methods=['POST'])
@limiter.limit('5 per minute')
def login():
    data = request.get_json() or {}
    identifier = data.get('email') or data.get('username') or ''
    password = data.get('password') or ''

    if not identifier or not password:
        return error_response('กรุณากรอกอีเมลและรหัสผ่าน', 400)

    result, err = auth_service.login_user(identifier, password)
    if err:
        admin_service.log_system_action(
            action_type='AUTH_LOGIN_FAILED',
            description=f'เข้าสู่ระบบล้มเหลวสำหรับ={identifier.strip().lower()[:120]}',
            user_id=None,
        )
        return error_response(err, 401)

    admin_service.log_system_action(
        action_type='AUTH_LOGIN_SUCCESS',
        description=f'เข้าสู่ระบบสำเร็จสำหรับ {result["user"]["email"]}',
        user_id=int(result['user']['user_id']),
    )
    return success_response(**result)


# API เข้าสู่ระบบด้วย Google OAuth Credential
@auth_bp.route('/google', methods=['POST'])
@limiter.limit('5 per minute')
def google_login():
    data = request.get_json() or {}
    credential = data.get('credential') or data.get('id_token') or ''

    if not credential:
        return error_response('กรุณาส่ง Google credential', 400)

    result, err = google_auth_service.login_with_google(credential)
    if err:
        admin_service.log_system_action(
            action_type='AUTH_GOOGLE_FAILED',
            description=f'เข้าสู่ระบบด้วย Google ล้มเหลว: {err[:120]}',
            user_id=None,
        )
        return error_response(err, 401)

    admin_service.log_system_action(
        action_type='AUTH_GOOGLE_SUCCESS',
        description=f'เข้าสู่ระบบด้วย Google สำเร็จสำหรับ {result["user"]["email"]}',
        user_id=int(result['user']['user_id']),
    )
    return success_response(**result)

# API ลงทะเบียนผู้ใช้งานใหม่
@auth_bp.route('/register', methods=['POST'])
@limiter.limit('3 per hour')
def register():
    data = request.get_json() or {}
    first_name = normalize_person_name(data.get('first_name'), required=True)
    last_name = normalize_person_name(data.get('last_name'))
    email = (data.get('email') or '').strip()
    email = normalize_email(email)
    password = data.get('password') or ''

    if not first_name or email is None or last_name is None or not password:
        return error_response('กรุณากรอกชื่อ อีเมล และรหัสผ่าน', 400)
    if len(password) < 6:
        return error_response('รหัสผ่านต้องมีอย่างน้อย 6 ตัวอักษร', 400)
    validation_error = password_error(password)
    if validation_error:
        return error_response(validation_error, 400)

    result, err = auth_service.register_user(first_name, last_name, email, password)
    if err:
        return error_response(err, 400)

    admin_service.log_system_action(
        action_type='AUTH_REGISTER',
        description=f'สมัครสมาชิกผู้ใช้ใหม่: {result["user"]["email"]}',
        user_id=int(result['user']['user_id']),
    )
    return success_response(message='สมัครสมาชิกสำเร็จ', **result, status=201)


# API ขอรหัส OTP สำหรับรีเซ็ตรหัสผ่านทางอีเมล
@auth_bp.route('/forgot-password', methods=['POST'])
@limiter.limit('10 per hour')
def forgot_password():
    data = request.get_json() or {}
    email = normalize_email(data.get('email'))
    if not email:
        return error_response('กรุณาระบุอีเมล', 400)
    
    ok, msg = auth_service.request_password_reset(email)
    if not ok:
        status_code = 404 if 'ไม่พบ' in msg else 400
        return error_response(msg, status_code)
    return success_response(message=msg)


# API ตรวจสอบความถูกต้องของรหัส OTP รีเซ็ตรหัสผ่าน
@auth_bp.route('/verify-otp', methods=['POST'])
@limiter.limit('10 per minute')
def verify_otp():
    data = request.get_json() or {}
    email = normalize_email(data.get('email'))
    otp = (data.get('otp') or '').strip()
    if not email or not otp:
        return error_response('กรุณาระบุอีเมลและรหัส OTP', 400)

    ok, msg = auth_service.verify_reset_otp(email, otp)
    if not ok:
        return error_response(msg, 400)
    return success_response(message=msg)


# API ตั้งรหัสผ่านใหม่โดยใช้รหัส OTP ที่ถูกต้อง
@auth_bp.route('/reset-password', methods=['POST'])
@limiter.limit('5 per hour')
def reset_password():
    data = request.get_json() or {}
    email = (data.get('email') or '').strip()
    email = normalize_email(email)
    otp = (data.get('otp') or '').strip()
    new_password = data.get('new_password') or ''
    if not email or not otp or not new_password:
        return error_response('กรุณากรอกอีเมล รหัส OTP และรหัสผ่านใหม่', 400)
    validation_error = password_error(new_password)
    if validation_error:
        return error_response(validation_error, 400)
    error = auth_service.reset_password_with_otp(email, otp, new_password)
    if error:
        return error_response(error, 400)
    return success_response(message='ตั้งรหัสผ่านใหม่สำเร็จ กรุณาเข้าสู่ระบบ')


# API ดึงข้อมูลส่วนตัวของผู้ใช้งานปัจจุบันที่เข้าสู่ระบบอยู่
@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def auth_me():
    user = auth_service.get_user_by_id(int(get_jwt_identity()))
    if not user:
        return error_response('ไม่พบผู้ใช้', 404)
    return success_response(user=user_to_dict(user))


# API เปลี่ยนรหัสผ่านของผู้ใช้งานปัจจุบัน
@auth_bp.route('/change-password', methods=['PUT'])
@jwt_required()
def change_password():
    claims = get_jwt()
    if claims.get('role') not in ('member', 'admin'):
        return error_response('สิทธิ์ไม่เพียงพอ', 403)

    data = request.get_json() or {}
    current_password = data.get('current_password') or ''
    new_password = data.get('new_password') or ''

    if not current_password or not new_password:
        return error_response('กรุณากรอกรหัสผ่านปัจจุบันและรหัสผ่านใหม่', 400)
    validation_error = password_error(new_password)
    if validation_error:
        return error_response(validation_error, 400)

    err = auth_service.change_password(
        int(get_jwt_identity()), current_password, new_password
    )
    if err:
        return error_response(err, 400)

    admin_service.log_system_action(
        action_type='AUTH_CHANGE_PASSWORD',
        description='ผู้ใช้งานเปลี่ยนรหัสผ่าน',
        user_id=int(get_jwt_identity()),
    )
    return success_response(message='เปลี่ยนรหัสผ่านสำเร็จ')
