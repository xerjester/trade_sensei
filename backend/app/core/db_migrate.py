"""Lightweight schema patches for existing databases (no Alembic)."""
from sqlalchemy import inspect, text

from app.core.database import db


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
        # Allow NULL for Google-only accounts on PostgreSQL
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
