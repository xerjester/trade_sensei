from functools import wraps

from flask import jsonify
from flask_jwt_extended import create_access_token, get_jwt, verify_jwt_in_request
from werkzeug.security import check_password_hash, generate_password_hash

from app.core.database import db
from app.models.schema import User


def hash_password(password: str) -> str:
    return generate_password_hash(password, method='scrypt')


def verify_password(password_hash: str, password: str) -> bool:
    return check_password_hash(password_hash, password)


def build_access_token(user: User) -> str:
    return create_access_token(
        identity=str(user.user_id),
        additional_claims={'role': user.role, 'email': user.email},
    )


def user_to_dict(user: User) -> dict:
    return {
        'user_id': user.user_id,
        'email': user.email,
        'role': user.role,
        'first_name': user.first_name,
        'last_name': user.last_name,
    }


def user_to_admin_dict(user: User) -> dict:
    return {
        **user_to_dict(user),
        'created_at': user.created_at.strftime('%Y-%m-%d %H:%M') if user.created_at else '',
    }


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        if get_jwt().get('role') != 'admin':
            return jsonify({'status': 'error', 'message': 'สิทธิ์ผู้ดูแลระบบเท่านั้น'}), 403
        return fn(*args, **kwargs)
    return wrapper


def seed_default_users() -> None:
    """Create the insecure convenience account only in explicit debug mode."""
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
