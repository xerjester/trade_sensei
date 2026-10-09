# โมดูลตรวจสอบและปรับรูปแบบข้อมูลนำเข้า (Input Validation)
import re

EMAIL_RE = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')
SYMBOL_RE = re.compile(r'^[A-Z0-9][A-Z0-9.\-]{0,14}$')


# ตรวจสอบและแปลงรูปแบบอีเมลให้เป็นตัวพิมพ์เล็กที่ถูกต้อง
def normalize_email(value: object) -> str | None:
    email = str(value or '').strip().lower()
    return email if len(email) <= 150 and EMAIL_RE.fullmatch(email) else None


# ตรวจสอบความถูกต้องของชื่อย่อหุ้น (เช่น PTT.BK, AAPL)
def normalize_symbol(value: object) -> str | None:
    symbol = str(value or '').strip().upper()
    return symbol if SYMBOL_RE.fullmatch(symbol) else None


# ตรวจสอบและกรองอักขระพิเศษออกจากชื่อผู้ใช้งาน
def normalize_person_name(value: object, *, required: bool = False) -> str | None:
    name = str(value or '').strip()
    if not name:
        return None if required else ''
    if len(name) > 100 or re.search(r'[<>\x00-\x1f\x7f]', name):
        return None
    return name


# ตรวจสอบความปลอดภัยและความยาวของรหัสผ่านตามเงื่อนไขที่กำหนด
def password_error(value: object) -> str | None:
    password = str(value or '')
    if len(password) < 8:
        return 'รหัสผ่านต้องมีอย่างน้อย 8 ตัวอักษร'
    if len(password) > 128:
        return 'รหัสผ่านยาวเกินกำหนด'
    if not re.search(r'[A-Za-z]', password) or not re.search(r'\d', password):
        return 'รหัสผ่านต้องมีตัวอักษรและตัวเลขอย่างน้อยอย่างละ 1 ตัว'
    return None
