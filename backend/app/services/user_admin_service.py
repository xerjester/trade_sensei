"""Admin user management."""
from app.core.database import db
from app.core.security import hash_password
from app.core.validation import normalize_email, normalize_person_name, password_error
from app.models import User


def list_users() -> list[dict]:
    users = User.query.order_by(User.created_at.desc()).all()
    return [
        {
            'user_id': u.user_id,
            'email': u.email,
            'first_name': u.first_name,
            'last_name': u.last_name,
            'role': u.role,
            'created_at': u.created_at.strftime('%Y-%m-%d %H:%M') if u.created_at else '',
        }
        for u in users
    ]


def _count_admins() -> int:
    return User.query.filter_by(role='admin').count()


def update_user(user_id: int, data: dict, acting_admin_id: int) -> str | None:
    user = db.session.get(User, user_id)
    if not user:
        return 'ไม่พบผู้ใช้'

    email = normalize_email(data.get('email') or user.email)
    first_name = normalize_person_name(
        data.get('first_name') or user.first_name, required=True
    )
    last_name = normalize_person_name(data.get('last_name') or user.last_name) or None
    role = (data.get('role') or user.role).strip().lower()
    new_password = data.get('new_password') or ''

    if not email:
        return 'รูปแบบอีเมลไม่ถูกต้อง'
    if not first_name:
        return 'รูปแบบชื่อไม่ถูกต้อง'
    if role not in ('member', 'admin'):
        return 'สิทธิ์ต้องเป็น member หรือ admin'
    if email != user.email:
        if User.query.filter_by(email=email).first():
            return 'อีเมลนี้ถูกใช้งานแล้ว'

    if user.user_id == acting_admin_id and role != 'admin':
        if _count_admins() <= 1:
            return 'ไม่สามารถเปลี่ยนสิทธิ์ตัวเองได้ (มี admin คนเดียวในระบบ)'

    if user.role == 'admin' and role != 'admin':
        if _count_admins() <= 1:
            return 'ต้องมีผู้ดูแลระบบอย่างน้อย 1 คน'

    user.email = email
    user.first_name = first_name
    user.last_name = last_name
    user.role = role

    if new_password:
        validation_error = password_error(new_password)
        if validation_error:
            return validation_error
        user.password_hash = hash_password(new_password)

    db.session.commit()
    return None


def delete_user(user_id: int, acting_admin_id: int) -> str | None:
    if user_id == acting_admin_id:
        return 'ไม่สามารถลบบัญชีของตัวเองได้'

    user = db.session.get(User, user_id)
    if not user:
        return 'ไม่พบผู้ใช้'

    if user.role == 'admin' and _count_admins() <= 1:
        return 'ไม่สามารถลบผู้ดูแลระบบคนสุดท้ายได้'

    db.session.delete(user)
    db.session.commit()
    return None
