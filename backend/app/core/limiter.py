# ระบบจำกัดอัตราการเรียกใช้งาน API (Rate Limiting) ป้องกันการยิง Request ถี่เกินไป
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# อินสแตนซ์ Limiter ส่วนกลาง กำหนดโควตาการเรียกใช้งานต่อ IP address
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=['3600 per hour', '120 per minute'],
)
