from functools import wraps

from flask import jsonify
from flask_jwt_extended import create_access_token, get_jwt, verify_jwt_in_request
from werkzeug.security import check_password_hash, generate_password_hash

from app.core.database import db
from app.models.schema import User


# แฮชรหัสผ่านด้วยอัลกอริทึม scrypt เพื่อความปลอดภัย
def hash_password(password: str) -> str:
    return generate_password_hash(password, method='scrypt')


# ตรวจสอบความถูกต้องของรหัสผ่านเทียบกับค่าแฮชที่บันทึกไว้
def verify_password(password_hash: str, password: str) -> bool:
    return check_password_hash(password_hash, password)


# สร้าง JWT Access Token สำหรับยืนยันตัวตน พร้อมแนบ role และ email
def build_access_token(user: User) -> str:
    return create_access_token(
        identity=str(user.user_id),
        additional_claims={'role': user.role, 'email': user.email},
    )


# แปลงข้อมูลผู้ใช้ให้อยู่ในรูป Dict พื้นฐานสำหรับส่งกลับไปยัง Frontend
def user_to_dict(user: User) -> dict:
    return {
        'user_id': user.user_id,
        'email': user.email,
        'role': user.role,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'username': user.username,
    }


# แปลงข้อมูลผู้ใช้พร้อมวันที่สร้างบัญชี สำหรับหน้าจัดการระบบของผู้ดูแลระบบ
def user_to_admin_dict(user: User) -> dict:
    return {
        **user_to_dict(user),
        'created_at': user.created_at.strftime('%Y-%m-%d %H:%M') if user.created_at else '',
    }


# Decorator สำหรับตรวจสอบสิทธิ์เฉพาะผู้ดูแลระบบ (Admin) เท่านั้น
def admin_required(fn):
    @wraps(fn)
    # ฟังก์ชันห่อหุ้มสำหรับตรวจเช็ค JWT Token และ Role Admin
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        if get_jwt().get('role') != 'admin':
            return jsonify({'status': 'error', 'message': 'สิทธิ์ผู้ดูแลระบบเท่านั้น'}), 403
        return fn(*args, **kwargs)
    return wrapper


# สร้างบัญชีผู้ดูแลระบบเริ่มต้นสำหรับทดสอบในโหมด Debug เท่านั้น
def seed_default_users() -> None:
    from app.core.config import Config
    if not Config.FLASK_DEBUG:
        return
    admin_email = 'admin@tradesensei.com'
    if User.query.filter_by(email=admin_email).first():
        return
    db.session.add(
        User(
            email=admin_email,
            first_name='Admin',
            last_name='System',
            password_hash=hash_password('admin'),
            role='admin',
        )
    )
    db.session.commit()
