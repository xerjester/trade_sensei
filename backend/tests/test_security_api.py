"""Adversarial API tests for common OWASP web risks."""
import pytest

from app.core.database import db
from app.models.schema import SystemLog

from conftest import auth_header, create_user


@pytest.mark.case('SEC-01', 'SQL Injection ใน Login ไม่สามารถข้าม Authentication')
def test_sec_01_login_sql_injection_fails(client):
    response = client.post('/api/auth/login', json={
        'email': "' OR 1=1 --",
        'password': "' OR 1=1 --",
    })

    assert response.status_code == 401
    assert response.get_json()['status'] == 'error'
    assert 'access_token' not in response.get_json()


@pytest.mark.case('SEC-02', 'SQL Injection ใน Stock Symbol ถูกปฏิเสธก่อน Query')
def test_sec_02_stock_symbol_sql_injection_rejected(client):
    response = client.get('/api/stock-data/AAPL%27%20OR%201=1--')

    assert response.status_code == 400
    assert response.get_json()['status'] == 'error'


@pytest.mark.case('SEC-03', 'SQL Injection ใน Log Filter ไม่เปลี่ยนเงื่อนไข Query')
def test_sec_03_log_filter_sql_injection_is_literal(app, client):
    admin_id = create_user(app, email='secure-admin@example.com', role='admin')
    with app.app_context():
        db.session.add(SystemLog(
            user_id=admin_id,
            action_type='SAFE_ACTION',
            description='safe log',
        ))
        db.session.commit()

    response = client.get(
        "/api/admin/logs?action_type=' OR 1=1 --",
        headers=auth_header(app, admin_id, role='admin', email='secure-admin@example.com'),
    )

    assert response.status_code == 200
    assert response.get_json()['data'] == []


@pytest.mark.case('SEC-04', 'JWT ปลอมหรือเสียรูปแบบถูกปฏิเสธ')
def test_sec_04_malformed_jwt_rejected(client):
    response = client.get(
        '/api/auth/me',
        headers={'Authorization': 'Bearer not-a-valid-jwt'},
    )

    assert response.status_code == 401
    assert response.get_json()['status'] == 'error'


@pytest.mark.case('SEC-05', 'Stored XSS ในชื่อผู้ใช้ถูกปฏิเสธ')
def test_sec_05_xss_name_rejected(client):
    response = client.post('/api/auth/register', json={
        'first_name': '<img src=x onerror=alert(1)>',
        'email': 'xss@example.com',
        'password': 'SecurePass1',
    })

    assert response.status_code == 400
    assert response.get_json()['status'] == 'error'


@pytest.mark.case('SEC-06', 'Payload เกิน 1 MB ถูกปฏิเสธ',
                  'Web server หรือ reverse proxy ควรกำหนด limit ซ้ำใน production')
def test_sec_06_oversized_payload_rejected(client):
    response = client.post('/api/auth/login', json={
        'email': 'large@example.com',
        'password': 'x' * (1024 * 1024 + 1),
    })

    assert response.status_code == 413
    assert response.get_json()['status'] == 'error'


@pytest.mark.case('SEC-07', 'Injection ผ่าน Email Format ถูกปฏิเสธ')
def test_sec_07_invalid_email_injection_rejected(client):
    response = client.post('/api/auth/register', json={
        'first_name': 'Safe Name',
        'email': "victim@example.com' OR '1'='1",
        'password': 'SecurePass1',
    })

    assert response.status_code == 400
    assert response.get_json()['status'] == 'error'


@pytest.mark.case('SEC-08', 'Member ไม่สามารถแก้ไขผู้ใช้ผ่าน IDOR')
def test_sec_08_member_cannot_update_another_user(app, client):
    member_id = create_user(app, email='attacker@example.com')
    victim_id = create_user(app, email='victim@example.com')

    response = client.put(
        f'/api/admin/users/{victim_id}',
        headers=auth_header(app, member_id, email='attacker@example.com'),
        json={'role': 'admin'},
    )

    assert response.status_code == 403


@pytest.mark.case('SEC-09', 'Admin ไม่สามารถลบบัญชีตนเอง')
def test_sec_09_admin_cannot_delete_self(app, client):
    admin_id = create_user(app, email='self-admin@example.com', role='admin')

    response = client.delete(
        f'/api/admin/users/{admin_id}',
        headers=auth_header(app, admin_id, role='admin', email='self-admin@example.com'),
    )

    assert response.status_code == 400
    assert response.get_json()['status'] == 'error'


@pytest.mark.case('SEC-10', 'Login ไม่เปิดเผยว่าอีเมลใดมีบัญชี')
def test_sec_10_login_errors_do_not_enumerate_accounts(app, client):
    create_user(app, email='known@example.com')

    known = client.post('/api/auth/login', json={
        'email': 'known@example.com', 'password': 'WrongPass1',
    })
    unknown = client.post('/api/auth/login', json={
        'email': 'unknown@example.com', 'password': 'WrongPass1',
    })

    assert known.status_code == unknown.status_code == 401
    assert known.get_json()['message'] == unknown.get_json()['message']


@pytest.mark.case('SEC-11', 'Forgot Password ตรวจสอบบัญชีผู้ใช้ในระบบ',
                  'ตรวจสอบการมีอยู่ของอีเมลในระบบก่อนส่ง OTP')
def test_sec_11_password_reset_validates_account(app, client):
    create_user(app, email='known-reset@example.com')

    known = client.post('/api/auth/forgot-password', json={'email': 'known-reset@example.com'})
    unknown = client.post('/api/auth/forgot-password', json={'email': 'unknown-reset@example.com'})

    assert known.status_code == 200
    assert unknown.status_code == 404
    assert 'ไม่พบ' in unknown.get_json()['message']


@pytest.mark.case('SEC-12', 'CORS ไม่อนุญาต Origin ที่ไม่อยู่ใน Allow-list')
def test_sec_12_untrusted_cors_origin_not_allowed(client):
    response = client.get('/api/stocks', headers={'Origin': 'https://evil.example'})

    assert response.status_code == 200
    assert 'Access-Control-Allow-Origin' not in response.headers


@pytest.mark.case('SEC-13', 'Response มี Content Security Policy')
def test_sec_13_content_security_policy_present(client):
    response = client.get('/')

    policy = response.headers['Content-Security-Policy']
    assert "default-src 'self'" in policy
    assert "object-src 'none'" in policy
    assert "frame-ancestors 'none'" in policy


@pytest.mark.case('SEC-14', '404 ไม่เปิดเผย Stack Trace หรือข้อมูลภายใน')
def test_sec_14_not_found_is_safe_json(client):
    response = client.get('/api/does-not-exist')
    body = response.get_json()

    assert response.status_code == 404
    assert body['status'] == 'error'
    assert 'traceback' not in str(body).lower()
    assert 'sqlalchemy' not in str(body).lower()


@pytest.mark.case('SEC-15', 'Production ปฏิเสธ Secret ที่สั้นหรือเป็นค่าเริ่มต้น')
def test_sec_15_production_rejects_weak_secrets(monkeypatch):
    from app.core.config import Config

    monkeypatch.setattr(Config, 'FLASK_DEBUG', False)
    monkeypatch.setattr(Config, 'SECRET_KEY', 'short')
    monkeypatch.setattr(Config, 'JWT_SECRET_KEY', 'short')

    with pytest.raises(RuntimeError):
        Config.validate()


@pytest.mark.case('SEC-16', 'รหัสผ่านถูก Hash และไม่จัดเก็บ Plaintext')
def test_sec_16_password_is_hashed(app, client):
    response = client.post('/api/auth/register', json={
        'first_name': 'Hash Test',
        'email': 'hash@example.com',
        'password': 'SecurePass1',
    })
    assert response.status_code == 201

    from app.models.schema import User
    with app.app_context():
        stored = User.query.filter_by(email='hash@example.com').one().password_hash
        assert stored != 'SecurePass1'
        assert 'SecurePass1' not in stored
        assert stored.startswith('scrypt:')


ADMIN_BOUNDARY_CASES = [
    ('GET', '/api/admin/users', None),
    ('POST', '/api/admin/stocks', {'symbol': 'AAPL', 'company_name': 'Apple'}),
    ('DELETE', '/api/admin/stocks/AAPL', None),
    ('POST', '/api/admin/run-scraper', {}),
    ('POST', '/api/admin/train-models', {}),
    ('POST', '/api/admin/train-models/sync', {}),
    ('PUT', '/api/admin/users/1', {'role': 'admin'}),
    ('DELETE', '/api/admin/users/1', None),
    ('GET', '/api/admin/logs', None),
    ('POST', '/api/fetch-stock', {'symbol': 'AAPL'}),
]


@pytest.mark.case('SEC-17', 'ทุก Admin Endpoint ปฏิเสธ JWT ของ Member')
@pytest.mark.parametrize('method,path,payload', ADMIN_BOUNDARY_CASES)
def test_sec_17_all_admin_endpoints_reject_member(app, client, method, path, payload):
    member_id = create_user(app)

    response = client.open(
        path,
        method=method,
        headers=auth_header(app, member_id),
        json=payload,
    )

    assert response.status_code == 403


@pytest.mark.case('SEC-18', 'Login Rate Limit ตัดคำขอครั้งที่ 6 ภายในหนึ่งนาที',
                  'Production หลาย instance ควรใช้ Redis เป็น shared limiter storage')
def test_sec_18_login_rate_limit_enforced(client):
    from app.core.limiter import limiter

    previous_state = limiter.enabled
    limiter.reset()
    limiter.enabled = True
    try:
        responses = [
            client.post('/api/auth/login', json={
                'email': 'rate@example.com', 'password': 'WrongPass1',
            })
            for _ in range(6)
        ]
        assert all(response.status_code == 401 for response in responses[:5])
        assert responses[5].status_code == 429
        assert responses[5].get_json()['status'] == 'error'
    finally:
        limiter.reset()
        limiter.enabled = previous_state


@pytest.mark.case('SEC-19', 'Admin Task ไม่รับ Command Injection จาก JSON')
def test_sec_19_admin_task_uses_fixed_subprocess_command(app, client, monkeypatch):
    from app.routers import admin as admin_router

    admin_id = create_user(app, email='command-admin@example.com', role='admin')
    captured = []
    monkeypatch.setattr(
        admin_router.subprocess,
        'Popen',
        lambda args, cwd=None: captured.append((args, cwd)),
    )

    response = client.post(
        '/api/admin/run-scraper',
        headers=auth_header(
            app, admin_id, role='admin', email='command-admin@example.com'
        ),
        json={'command': 'rm -rf /', 'symbol': '; whoami'},
    )

    assert response.status_code == 202
    assert len(captured) == 1
    assert captured[0][0][0] == 'python'
    assert captured[0][0][1].endswith('scripts/scraper.py')
    assert len(captured[0][0]) == 2


@pytest.mark.case('SEC-20', 'Register ป้องกัน Mass Assignment เป็น Admin')
def test_sec_20_register_cannot_assign_admin_role(client):
    response = client.post('/api/auth/register', json={
        'first_name': 'Normal User',
        'email': 'mass-assignment@example.com',
        'password': 'SecurePass1',
        'role': 'admin',
        'is_admin': True,
    })

    assert response.status_code == 201
    assert response.get_json()['user']['role'] == 'member'
