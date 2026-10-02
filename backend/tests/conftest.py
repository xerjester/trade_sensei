"""Shared isolated Flask application and helpers for API tests.

Tests use a temporary SQLite database and never call external Yahoo, Gemini,
Resend, scheduler, or Prophet services.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
from flask_jwt_extended import create_access_token
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.compiler import compiles


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


@compiles(JSONB, 'sqlite')
def compile_jsonb_for_sqlite(_type, _compiler, **_kwargs):
    """Use SQLite's JSON affinity for the PostgreSQL JSONB model field in tests."""
    return 'JSON'


@pytest.fixture()
def app(monkeypatch, tmp_path):
    import app as app_package
    from app.core.config import Config
    from app.core.database import db

    # Keep the factory close to production while isolating state and background work.
    Config.SQLALCHEMY_DATABASE_URI = f"sqlite:///{tmp_path / 'tradesensei-test.db'}"
    Config.SQLALCHEMY_ENGINE_OPTIONS = {'connect_args': {'check_same_thread': False}}
    Config.FLASK_DEBUG = True
    Config.SECRET_KEY = 'test-secret-key-at-least-thirty-two-characters'
    Config.JWT_SECRET_KEY = 'test-jwt-secret-key-at-least-thirty-two-chars'
    Config.CORS_ORIGINS = ('http://localhost:5500',)
    monkeypatch.setattr(app_package, 'start_scheduler', lambda _app: None)

    flask_app = app_package.create_app()
    flask_app.config.update(TESTING=True, RATELIMIT_ENABLED=False)

    yield flask_app

    with flask_app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


def create_user(app, *, email='member@example.com', role='member', password='SecurePass1'):
    """Persist a user suitable for authorization tests."""
    from app.core.database import db
    from app.core.security import hash_password
    from app.models.schema import User

    with app.app_context():
        user = User(
            first_name='Test',
            last_name='User',
            email=email,
            password_hash=hash_password(password),
            role=role,
        )
        db.session.add(user)
        db.session.commit()
        return user.user_id


def auth_header(app, user_id, role='member', email='member@example.com'):
    """Create a role-bearing JWT header matching TradeSensei authentication."""
    with app.app_context():
        token = create_access_token(
            identity=str(user_id),
            additional_claims={'role': role, 'email': email},
        )
    return {'Authorization': f'Bearer {token}'}


def pytest_collection_modifyitems(items):
    """Copy @pytest.mark.case metadata onto reports for the final case summary."""
    for item in items:
        marker = item.get_closest_marker('case')
        if not marker:
            continue
        case_id = marker.args[0]
        title = marker.args[1]
        caution = marker.args[2] if len(marker.args) > 2 else ''
        item.user_properties.extend([
            ('case_id', case_id),
            ('case_title', title),
            ('case_caution', caution),
        ])


def pytest_terminal_summary(terminalreporter):
    """Print an audit-friendly pass/fail table instead of only aggregate dots."""
    rows = []
    for status_key, label in (
        ('passed', 'PASS'),
        ('failed', 'FAIL'),
        ('error', 'ERROR'),
        ('skipped', 'SKIP'),
    ):
        for report in terminalreporter.stats.get(status_key, []):
            if report.when != 'call' and not report.failed:
                continue
            metadata = dict(report.user_properties)
            case_id = metadata.get('case_id')
            if not case_id:
                continue
            rows.append({
                'id': case_id,
                'title': metadata.get('case_title', report.nodeid),
                'caution': metadata.get('case_caution', ''),
                'status': label,
            })

    if not rows:
        return

    rows.sort(key=lambda row: row['id'])
    terminalreporter.write_sep('=', 'ผลการทดสอบราย Test Case')
    for row in rows:
        terminalreporter.write_line(
            f"{row['id']:<7} [{row['status']:<5}] {row['title']}"
        )

    cautions = [row for row in rows if row['caution']]
    if cautions:
        terminalreporter.write_sep('-', 'จุดที่ควรระวัง')
        for row in cautions:
            terminalreporter.write_line(f"{row['id']}: {row['caution']}")

    counts = {label: sum(row['status'] == label for row in rows)
              for label in ('PASS', 'FAIL', 'ERROR', 'SKIP')}
    terminalreporter.write_sep('-', 'สรุป')
    terminalreporter.write_line(
        f"ทั้งหมด {len(rows)} เคส | ผ่าน {counts['PASS']} | "
        f"ไม่ผ่าน {counts['FAIL']} | ผิดพลาด {counts['ERROR']} | ข้าม {counts['SKIP']}"
    )
