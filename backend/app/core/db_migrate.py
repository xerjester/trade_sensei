# สคริปต์อัปเดตโครงสร้างฐานข้อมูลแบบอัตโนมัติ (Schema Migration)
from sqlalchemy import inspect, text

from app.core.database import db


# ตรวจสอบและเพิ่มคอลัมน์ google_id และปรับ password_hash ให้เป็น nullable สำหรับการล็อกอินผ่าน Google
def apply_user_auth_columns() -> None:
    inspector = inspect(db.engine)
    if 'users' not in inspector.get_table_names():
        return

    columns = {col['name'] for col in inspector.get_columns('users')}
    statements = []

    if 'google_id' not in columns:
        statements.append(
            'ALTER TABLE users ADD COLUMN google_id VARCHAR(128) UNIQUE'
        )
    if 'password_hash' in columns:
        # อนุญาตให้คอลัมน์ password_hash เป็นค่าว่างได้ สำหรับผู้ใช้ที่เข้าสู่ระบบผ่าน Google
        statements.append(
            'ALTER TABLE users ALTER COLUMN password_hash DROP NOT NULL'
        )

    for stmt in statements:
        try:
            db.session.execute(text(stmt))
        except Exception:
            db.session.rollback()
            continue
    db.session.commit()
