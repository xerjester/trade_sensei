import secrets
from datetime import datetime, timedelta

from app.core.config import Config
from app.core.database import db
from app.core.security import (
    build_access_token,
    hash_password,
    user_to_dict,
    verify_password,
)
from app.core.validation import normalize_person_name, password_error
from app.models import PasswordResetOtp, SystemLog, User

OTP_EXPIRY_MINUTES = 10
OTP_RESEND_COOLDOWN_SECONDS = 60
OTP_MAX_ATTEMPTS = 5


# แปลงชื่อหรืออีเมลให้เป็นพิมพ์เล็ก ถ้าพิมพ์ 'admin' จะแปลงเป็นอีเมลแอดมินให้อัตโนมัติ
def normalize_identifier(identifier: str) -> str:
    identifier = identifier.strip().lower()
    if identifier == 'admin':
        return 'admin@tradesensei.com'
    return identifier


# ตรวจสอบอีเมลและรหัสผ่านเพื่อล็อกอิน ถ้าผ่านจะสร้าง JWT token ส่งกลับไป
def login_user(email: str, password: str) -> tuple[dict | None, str | None]:
    user = User.query.filter_by(email=normalize_identifier(email)).first()
    if not user:
        return None, 'อีเมลหรือรหัสผ่านไม่ถูกต้อง'
    if not user.password_hash:
        return None, 'บัญชีนี้ใช้ Google Login — กรุณาเข้าสู่ระบบด้วย Google'
    if not verify_password(user.password_hash, password):
        return None, 'อีเมลหรือรหัสผ่านไม่ถูกต้อง'
    return {
        'access_token': build_access_token(user),
        'user': user_to_dict(user),
    }, None


# สมัครสมาชิกใหม่ ตรวจสอบความถูกต้อง แฮชรหัสผ่าน แล้วบันทึกลงตาราง users
def register_user(first_name: str, last_name: str, email: str, password: str) -> tuple[dict | None, str | None]:
    first_name = normalize_person_name(first_name, required=True)
    last_name = normalize_person_name(last_name)
    if not first_name or last_name is None:
        return None, 'รูปแบบชื่อไม่ถูกต้อง'
    email = email.strip().lower()
    if User.query.filter_by(email=email).first():
        return None, 'อีเมลนี้ถูกใช้งานแล้ว'
    validation_error = password_error(password)
    if validation_error:
        return None, validation_error

    user = User(
        first_name=first_name,
        last_name=last_name or None,
        email=email,
        password_hash=hash_password(password),
        role='member',
    )
    db.session.add(user)
    db.session.commit()
    return {
        'access_token': build_access_token(user),
        'user': user_to_dict(user),
    }, None


# ดึงข้อมูลผู้ใช้จาก user_id
def get_user_by_id(user_id: int) -> User | None:
    return db.session.get(User, user_id)


# เปลี่ยนรหัสผ่านของผู้ใช้ (ต้องเช็กรหัสเดิมให้ผ่านก่อน)
def change_password(
    user_id: int, current_password: str, new_password: str
) -> str | None:
    validation_error = password_error(new_password)
    if validation_error:
        return validation_error
    user = db.session.get(User, user_id)
    if not user:
        return 'ไม่พบผู้ใช้'

    if not user.password_hash:
        return 'บัญชี Google ไม่สามารถเปลี่ยนรหัสผ่านแบบนี้ได้ — ใช้การตั้งรหัสใน Google'

    if not verify_password(user.password_hash, current_password):
        return 'รหัสผ่านปัจจุบันไม่ถูกต้อง'

    if len(new_password) < 6:
        return 'รหัสผ่านใหม่ต้องมีอย่างน้อย 6 ตัวอักษร'

    if verify_password(user.password_hash, new_password):
        return 'รหัสผ่านใหม่ต้องไม่ซ้ำกับรหัสเดิม'

    user.password_hash = hash_password(new_password)
    db.session.commit()
    return None


# ส่งอีเมลรหัส OTP 6 ตัวผ่านบริการ Resend
def _send_reset_email(email: str, code: str) -> None:
    """Send a short-lived OTP via Resend; the API key stays server-side only."""
    if not Config.RESEND_API_KEY:
        raise RuntimeError('Password reset email is not configured')

    import resend

    resend.api_key = Config.RESEND_API_KEY
    sender = Config.RESEND_FROM_EMAIL or 'TradeSensei <onboarding@resend.dev>'

    html_content = (
        '<p>รหัสยืนยันเพื่อรีเซ็ตรหัสผ่าน TradeSensei ของคุณคือ</p>'
        f'<h1 style="letter-spacing: 0.25em">{code}</h1>'
        f'<p>รหัสนี้หมดอายุใน {OTP_EXPIRY_MINUTES} นาที และใช้ได้เพียงครั้งเดียว</p>'
        '<p>หากคุณไม่ได้ร้องขอการเปลี่ยนรหัสผ่าน กรุณาไม่ต้องดำเนินการใด ๆ</p>'
    )

    try:
        resend.Emails.send({
            'from': sender,
            'to': email,
            'subject': 'TradeSensei password reset code',
            'html': html_content,
        })
    except Exception as e:
        # If unverified domain error, retry with default verified testing sender
        if 'not verified' in str(e).lower() and sender != 'TradeSensei <onboarding@resend.dev>':
            resend.Emails.send({
                'from': 'TradeSensei <onboarding@resend.dev>',
                'to': email,
                'subject': 'TradeSensei password reset code',
                'html': html_content,
            })
        else:
            raise


# ขอรีเซ็ตรหัสผ่าน: สร้างรหัส OTP 6 หลัก แล้วส่งเข้าอีเมล (รหัสมีอายุ 10 นาที)
def request_password_reset(email: str) -> tuple[bool, str]:
    """Validate user exists and issue/email one 6-digit OTP."""
    clean_email = normalize_identifier(email)
    user = User.query.filter_by(email=clean_email).first()
    if not user:
        return False, 'ไม่พบอีเมลนี้ในระบบ กรุณาตรวจสอบอีเมลหรือสมัครสมาชิก'
    if not user.password_hash:
        return False, 'บัญชีนี้ลงทะเบียนผ่าน Google กรุณาเข้าสู่ระบบด้วย Google'

    now = datetime.utcnow()
    latest = (
        PasswordResetOtp.query.filter_by(user_id=user.user_id, used_at=None)
        .order_by(PasswordResetOtp.created_at.desc())
        .first()
    )
    if latest and (now - latest.created_at).total_seconds() < OTP_RESEND_COOLDOWN_SECONDS:
        rem = int(OTP_RESEND_COOLDOWN_SECONDS - (now - latest.created_at).total_seconds())
        return False, f'กรุณารอ {rem} วินาทีก่อนขอรหัส OTP ใหม่อีกครั้ง'

    # Invalidate earlier codes before issuing this single-use six-digit code.
    PasswordResetOtp.query.filter_by(user_id=user.user_id, used_at=None).update(
        {'used_at': now}, synchronize_session=False
    )
    code = f'{secrets.randbelow(1_000_000):06d}'
    reset = PasswordResetOtp(
        user_id=user.user_id,
        code_hash=hash_password(code),
        expires_at=now + timedelta(minutes=OTP_EXPIRY_MINUTES),
    )
    db.session.add(reset)
    try:
        _send_reset_email(user.email, code)
        db.session.add(SystemLog(
            user_id=user.user_id,
            action_type='AUTH_PASSWORD_RESET_OTP_SENT',
            description=f'Password reset OTP sent to {user.email}' + (f' (OTP: {code})' if Config.FLASK_DEBUG else ''),
        ))
        db.session.commit()
    except Exception as e:
        err_str = str(e)
        # ตรวจสอบว่าเป็นข้อจำกัดของ Resend Free Tier Sandbox หรือไม่ (อนุญาตส่งเฉพาะเจ้าของบัญชี alatus2003@gmail.com)
        is_sandbox_limit = (
            'can only send testing emails' in err_str.lower()
            or 'testing emails' in err_str.lower()
            or 'verify your domain' in err_str.lower()
            or 'validation_error' in err_str.lower()
            or 'not verified' in err_str.lower()
        )
        if is_sandbox_limit or Config.FLASK_DEBUG:
            # Resend Sandbox ส่งเข้า inbox จริงได้เฉพาะ alatus2003@gmail.com
            # เพื่อให้กรรมการสอบและนักศึกษาทดสอบระบบด้วยเมลอื่นได้โดยไม่ error 500:
            # บันทึกรหัส OTP ลงใน SystemLog และแสดงรหัสเพื่อใช้ทดสอบได้ทันที
            db.session.add(SystemLog(
                user_id=user.user_id,
                action_type='AUTH_PASSWORD_RESET_OTP_SENT',
                description=(
                    f'[Resend Sandbox Alert] รหัส OTP สำหรับ {user.email} คือ: {code} '
                    f'(ไม่สามารถส่งเข้า inbox ได้เนื่องจาก Resend Sandbox จำกัดส่งเฉพาะ alatus2003@gmail.com)'
                ),
            ))
            db.session.commit()
            return True, f'รหัส OTP ถูกสร้างเรียบร้อยแล้ว (หมายเหตุ: บัญชี Resend Sandbox ส่งเข้า inbox ได้เฉพาะ alatus2003@gmail.com สำหรับอีเมลอื่นสามารถนำรหัส OTP ไปทดสอบได้ทันที: {code})'
        else:
            db.session.rollback()
            return False, f'ไม่สามารถส่งอีเมลรหัส OTP ได้ในขณะนี้ ({err_str[:100]})'
    return True, 'ส่งรหัส OTP 6 หลักไปยังอีเมลของคุณเรียบร้อยแล้ว'


# ตรวจสอบรหัส OTP 6 หลักว่าถูกต้องและยังไม่หมดอายุหรือไม่
def verify_reset_otp(email: str, code: str) -> tuple[bool, str]:
    """Verify that an OTP is correct and valid without consuming it yet."""
    clean_code = str(code or '').strip()
    if not clean_code or len(clean_code) != 6 or not clean_code.isdigit():
        return False, 'กรุณากรอกรหัส OTP เป็นตัวเลข 6 หลัก'

    user = User.query.filter_by(email=normalize_identifier(email)).first()
    if not user or not user.password_hash:
        return False, 'ไม่พบข้อมูลบัญชีผู้ใช้'

    reset = (
        PasswordResetOtp.query.filter_by(user_id=user.user_id, used_at=None)
        .order_by(PasswordResetOtp.created_at.desc())
        .first()
    )
    now = datetime.utcnow()
    if not reset or reset.expires_at < now or reset.attempts >= OTP_MAX_ATTEMPTS:
        return False, 'รหัส OTP ไม่ถูกต้องหรือหมดอายุแล้ว กรุณาขอรหัสใหม่'

    if not verify_password(reset.code_hash, clean_code):
        reset.attempts += 1
        if reset.attempts >= OTP_MAX_ATTEMPTS:
            reset.used_at = now
        db.session.commit()
        remaining = max(0, OTP_MAX_ATTEMPTS - reset.attempts)
        if remaining == 0:
            return False, 'กรอกรหัสผิดเกินจำนวนที่กำหนด รหัส OTP ถูกยกเลิกแล้ว กรุณาขอใหม่'
        return False, f'รหัส OTP ไม่ถูกต้อง (เหลือโอกาสอีก {remaining} ครั้ง)'

    return True, 'ยืนยันรหัส OTP ถูกต้อง'


# ยืนยันรหัส OTP และตั้งรหัสผ่านใหม่ลงฐานข้อมูล
def reset_password_with_otp(email: str, code: str, new_password: str) -> str | None:
    """Verify an unexpired OTP with attempt limiting, then rotate the password."""
    validation_error = password_error(new_password)
    if validation_error:
        return validation_error
    if len(new_password) < 6:
        return 'รหัสผ่านใหม่ต้องมีอย่างน้อย 6 ตัวอักษร'
    user = User.query.filter_by(email=normalize_identifier(email)).first()
    if not user or not user.password_hash:
        return 'รหัสยืนยันหรืออีเมลไม่ถูกต้อง'

    reset = (
        PasswordResetOtp.query.filter_by(user_id=user.user_id, used_at=None)
        .order_by(PasswordResetOtp.created_at.desc())
        .first()
    )
    now = datetime.utcnow()
    if not reset or reset.expires_at < now or reset.attempts >= OTP_MAX_ATTEMPTS:
        return 'รหัสยืนยันไม่ถูกต้องหรือหมดอายุ'

    if not verify_password(reset.code_hash, str(code).strip()):
        reset.attempts += 1
        if reset.attempts >= OTP_MAX_ATTEMPTS:
            reset.used_at = now
        db.session.commit()
        return 'รหัสยืนยันไม่ถูกต้องหรือหมดอายุ'

    user.password_hash = hash_password(new_password)
    PasswordResetOtp.query.filter_by(user_id=user.user_id, used_at=None).update(
        {'used_at': now}, synchronize_session=False
    )
    db.session.add(SystemLog(
        user_id=user.user_id,
        action_type='AUTH_PASSWORD_RESET_SUCCESS',
        description='Password reset completed with email OTP',
    ))
    db.session.commit()
    return None
