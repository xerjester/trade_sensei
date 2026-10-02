"""Google Sign-In (ID token verification)."""
import secrets

from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

from app.core.config import Config
from app.core.database import db
from app.core.security import build_access_token, hash_password, user_to_dict
from app.models import User


def _unusable_password_hash() -> str:
    """Placeholder for OAuth-only accounts (cannot log in with password)."""
    return hash_password(secrets.token_urlsafe(32))


def _is_configured_client_id() -> bool:
    if not Config.GOOGLE_CLIENT_ID:
        return False
    lower = Config.GOOGLE_CLIENT_ID.strip().lower()
    return not any(p in lower for p in ('your_google', 'your_', 'placeholder', 'example', 'change_me'))


def verify_google_id_token(token: str) -> dict | None:
    if not _is_configured_client_id():
        return None
    try:
        return id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            Config.GOOGLE_CLIENT_ID,
        )
    except ValueError:
        return None


def login_with_google(id_token_str: str) -> tuple[dict | None, str | None]:
    if not _is_configured_client_id():
        return None, 'ยังไม่ได้ตั้งค่า Google Login (GOOGLE_CLIENT_ID)'

    claims = verify_google_id_token(id_token_str)
    if not claims:
        return None, 'Google token ไม่ถูกต้องหรือหมดอายุ'

    google_sub = claims.get('sub')
    email = (claims.get('email') or '').strip().lower()
    if not google_sub or not email:
        return None, 'บัญชี Google ไม่มีอีเมลที่ใช้ยืนยันได้'

    if not claims.get('email_verified', False):
        return None, 'กรุณายืนยันอีเมล Google ก่อนเข้าสู่ระบบ'

    user = User.query.filter_by(google_id=google_sub).first()
    if not user:
        user = User.query.filter_by(email=email).first()

    given = (claims.get('given_name') or '').strip()
    family = (claims.get('family_name') or '').strip()
    full_name = (claims.get('name') or '').strip()

    if user:
        user.google_id = google_sub
        if given and not user.first_name:
            user.first_name = given
        if family and not user.last_name:
            user.last_name = family
        if not user.first_name and full_name:
            user.first_name = full_name.split()[0]
    else:
        user = User(
            email=email,
            google_id=google_sub,
            first_name=given or (full_name.split()[0] if full_name else 'Member'),
            last_name=family or None,
            password_hash=_unusable_password_hash(),
            role='member',
        )
        db.session.add(user)

    db.session.commit()

    return {
        'access_token': build_access_token(user),
        'user': user_to_dict(user),
    }, None
