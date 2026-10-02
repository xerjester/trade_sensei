"""Success-path coverage for the remaining TradeSensei API workflows."""
from datetime import date, datetime, timedelta

import pytest

from app.core.database import db
from app.core.security import hash_password
from app.models.schema import HistoricalPrice, PasswordResetOtp, Stock, User

from conftest import auth_header, create_user


def create_admin(app):
    admin_id = create_user(app, email='workflow-admin@example.com', role='admin')
    return admin_id, auth_header(
        app, admin_id, role='admin', email='workflow-admin@example.com'
    )


def create_stock(app, symbol='AAPL'):
    with app.app_context():
        stock = Stock(symbol=symbol, company_name='Fixture Corp', category='Technology')
        db.session.add(stock)
        db.session.commit()
        return stock.stock_id


@pytest.mark.case('API-01', 'Auth Config เปิดเผยเฉพาะค่าที่อนุญาต')
def test_api_01_auth_config_is_public_and_safe(client):
    response = client.get('/api/auth/config')

    assert response.status_code == 200
    assert set(response.get_json()['data']) == {'google_client_id', 'google_login_enabled'}
    assert 'secret' not in str(response.get_json()).lower()


@pytest.mark.case('API-02', 'Database Health Check เชื่อมต่อฐานข้อมูลได้')
def test_api_02_database_health(client):
    response = client.get('/test-db')

    assert response.status_code == 200
    assert response.get_json()['status'] == 'success'


@pytest.mark.case('API-03', 'Member เปลี่ยนรหัสผ่านและ Login ด้วยรหัสใหม่')
def test_api_03_change_password(app, client):
    member_id = create_user(app, password='SecurePass1')
    response = client.put(
        '/api/auth/change-password',
        headers=auth_header(app, member_id),
        json={'current_password': 'SecurePass1', 'new_password': 'NewSecure2'},
    )

    assert response.status_code == 200
    assert client.post('/api/auth/login', json={
        'email': 'member@example.com', 'password': 'SecurePass1',
    }).status_code == 401
    assert client.post('/api/auth/login', json={
        'email': 'member@example.com', 'password': 'NewSecure2',
    }).status_code == 200


@pytest.mark.case('API-04', 'OTP ที่ถูกต้องเปลี่ยนรหัสผ่านได้ครั้งเดียว',
                  'การส่ง OTP ผ่าน Resend จริงอยู่ใน controlled integration test')
def test_api_04_reset_password_with_single_use_otp(app, client):
    member_id = create_user(app, email='otp@example.com')
    with app.app_context():
        db.session.add(PasswordResetOtp(
            user_id=member_id,
            code_hash=hash_password('123456'),
            expires_at=datetime.utcnow() + timedelta(minutes=10),
        ))
        db.session.commit()

    payload = {
        'email': 'otp@example.com',
        'otp': '123456',
        'new_password': 'ChangedPass2',
    }
    first = client.post('/api/auth/reset-password', json=payload)
    second = client.post('/api/auth/reset-password', json=payload)

    assert first.status_code == 200
    assert second.status_code == 400
    assert client.post('/api/auth/login', json={
        'email': 'otp@example.com', 'password': 'ChangedPass2',
    }).status_code == 200


@pytest.mark.case('API-04B', 'Verify OTP ตรวจสอบความถูกต้องของรหัส 6 หลัก')
def test_api_04b_verify_otp_endpoint(app, client):
    member_id = create_user(app, email='verify-otp@example.com')
    with app.app_context():
        db.session.add(PasswordResetOtp(
            user_id=member_id,
            code_hash=hash_password('654321'),
            expires_at=datetime.utcnow() + timedelta(minutes=10),
        ))
        db.session.commit()

    # Empty/invalid format
    res_empty = client.post('/api/auth/verify-otp', json={'email': 'verify-otp@example.com', 'otp': ''})
    assert res_empty.status_code == 400

    # Wrong OTP
    bad = client.post('/api/auth/verify-otp', json={'email': 'verify-otp@example.com', 'otp': '000000'})
    assert bad.status_code == 400
    assert 'ไม่ถูกต้อง' in bad.get_json()['message']

    # Correct OTP
    good = client.post('/api/auth/verify-otp', json={'email': 'verify-otp@example.com', 'otp': '654321'})
    assert good.status_code == 200
    assert good.get_json()['status'] == 'success'


@pytest.mark.case('API-05', 'Google Login ปฏิเสธ Request ที่ไม่มี Credential')
def test_api_05_google_login_requires_credential(client):
    response = client.post('/api/auth/google', json={})

    assert response.status_code == 400
    assert response.get_json()['status'] == 'error'


@pytest.mark.case('API-06', 'Member เรียก Forecast และรับผล 7 วันจาก D5',
                  'Prophet ถูก mock; ความแม่นยำของโมเดลทดสอบแยกด้วย fixture ระยะยาว')
def test_api_06_prediction_success(app, client, monkeypatch):
    from app.routers import predictions as prediction_router

    stock_id = create_stock(app)
    member_id = create_user(app)
    forecast = [{
        'predict_date': f'2026-08-{day:02d}',
        'predicted_close': 100 + day,
        'predicted_lower': 99 + day,
        'predicted_upper': 101 + day,
    } for day in range(8, 15)]
    monkeypatch.setattr(
        prediction_router.predictor_service,
        'run_prophet_forecast',
        lambda requested_id: (forecast, False) if requested_id == stock_id else None,
    )
    monkeypatch.setattr(
        prediction_router.predictor_service,
        'get_forecast_quality',
        lambda _stock_id: {'mae': 1.2, 'mape_pct': 2.3},
    )

    response = client.get('/api/predict/AAPL', headers=auth_header(app, member_id))

    assert response.status_code == 200
    assert len(response.get_json()['data']['dates']) == 7
    assert response.get_json()['quality']['mae'] == 1.2


@pytest.mark.case('API-07', 'Member เรียก Deep Analysis ได้')
def test_api_07_deep_analysis_success(app, client, monkeypatch):
    from app.routers import analysis as analysis_router

    member_id = create_user(app)
    expected = {'symbol': 'AAPL', 'trend': 'up', 'sentiment': {'label': 'Neutral'}}
    monkeypatch.setattr(
        analysis_router.analysis_service,
        'get_deep_analysis',
        lambda symbol: expected if symbol == 'AAPL' else None,
    )

    response = client.get('/api/analysis/aapl', headers=auth_header(app, member_id))

    assert response.status_code == 200
    assert response.get_json()['data'] == expected


@pytest.mark.case('API-08', 'Member จำลอง Backtest เทียบเงินฝากได้')
def test_api_08_backtest_success(app, client):
    stock_id = create_stock(app)
    member_id = create_user(app)
    today = datetime.utcnow().date()
    with app.app_context():
        db.session.add_all([
            HistoricalPrice(
                stock_id=stock_id, date=today - timedelta(days=20),
                open_price=95, high_price=101, low_price=94, close_price=100, volume=1000,
            ),
            HistoricalPrice(
                stock_id=stock_id, date=today - timedelta(days=1),
                open_price=108, high_price=112, low_price=107, close_price=110, volume=1200,
            ),
        ])
        db.session.commit()

    response = client.post(
        '/api/backtest/AAPL',
        headers=auth_header(app, member_id),
        json={'months': 1, 'initial_amount': 100000},
    )

    assert response.status_code == 200
    assert response.get_json()['data']['stock']['return_pct'] == 10.0
    assert 'deposit_benchmark' in response.get_json()['data']


@pytest.mark.case('API-09', 'Member ส่งคำถาม Copilot และระบบบันทึกผล')
def test_api_09_copilot_chat_success(app, client, monkeypatch):
    from app.routers import chatbot as chatbot_router

    member_id = create_user(app)
    monkeypatch.setattr(
        chatbot_router.copilot_service,
        'chat',
        lambda user_id, symbol, message: {
            'response': f'{symbol}: grounded fixture',
            'provider': 'AI_Copilot_Grounded',
            'symbol': symbol,
        },
    )

    response = client.post(
        '/api/copilot/chat',
        headers=auth_header(app, member_id),
        json={'symbol': 'AAPL', 'message': 'แนวโน้มเป็นอย่างไร'},
    )

    assert response.status_code == 200
    assert response.get_json()['data']['provider'] == 'AI_Copilot_Grounded'


@pytest.mark.case('API-10', 'Admin ลบหุ้นออกจาก Master Data')
def test_api_10_admin_deletes_stock(app, client):
    create_stock(app)
    _admin_id, headers = create_admin(app)

    response = client.delete('/api/admin/stocks/AAPL', headers=headers)

    assert response.status_code == 200
    with app.app_context():
        assert Stock.query.filter_by(symbol='AAPL').count() == 0


@pytest.mark.case('API-11', 'Admin ดูรายชื่อและแก้ไขข้อมูลผู้ใช้')
def test_api_11_admin_lists_and_updates_user(app, client):
    target_id = create_user(app, email='target@example.com')
    _admin_id, headers = create_admin(app)

    listing = client.get('/api/admin/users', headers=headers)
    updated = client.put(
        f'/api/admin/users/{target_id}',
        headers=headers,
        json={'first_name': 'Updated', 'role': 'member'},
    )

    assert listing.status_code == 200
    assert any(user['email'] == 'target@example.com' for user in listing.get_json()['data'])
    assert updated.status_code == 200
    assert updated.get_json()['user']['first_name'] == 'Updated'


@pytest.mark.case('API-12', 'Admin ลบบัญชีผู้ใช้อื่นได้')
def test_api_12_admin_deletes_user(app, client):
    target_id = create_user(app, email='delete-me@example.com')
    _admin_id, headers = create_admin(app)

    response = client.delete(f'/api/admin/users/{target_id}', headers=headers)

    assert response.status_code == 200
    with app.app_context():
        assert db.session.get(User, target_id) is None


@pytest.mark.case('API-13', 'Admin Fetch Stock เรียก Data Service')
def test_api_13_fetch_stock_success(app, client, monkeypatch):
    from app.routers import stocks as stocks_router

    _admin_id, headers = create_admin(app)
    monkeypatch.setattr(
        stocks_router.stock_service,
        'fetch_stock_from_yfinance',
        lambda symbol: (25, None) if symbol == 'AAPL' else (0, 'not found'),
    )

    response = client.post('/api/fetch-stock', headers=headers, json={'symbol': 'aapl'})

    assert response.status_code == 200
    assert response.get_json()['new_records_added'] == 25


@pytest.mark.case('API-14', 'Admin เริ่ม Scraper แบบ Background',
                  'ตรวจการ dispatch เท่านั้น ไม่เรียก Yahoo Finance จริง')
def test_api_14_admin_starts_scraper(app, client, monkeypatch):
    from app.routers import admin as admin_router

    _admin_id, headers = create_admin(app)
    calls = []
    monkeypatch.setattr(
        admin_router.subprocess,
        'Popen',
        lambda args, cwd=None: calls.append((args, cwd)),
    )

    response = client.post('/api/admin/run-scraper', headers=headers, json={})

    assert response.status_code == 202
    assert calls and calls[0][0][0] == 'python'


@pytest.mark.case('API-15', 'Admin เริ่ม Batch Train แบบ Background',
                  'ตรวจการ dispatch เท่านั้น ไม่เทรน Prophet จริง')
def test_api_15_admin_starts_batch_train(app, client, monkeypatch):
    from app.routers import admin as admin_router

    _admin_id, headers = create_admin(app)
    calls = []
    monkeypatch.setattr(
        admin_router.subprocess,
        'Popen',
        lambda args, cwd=None: calls.append((args, cwd)),
    )

    response = client.post('/api/admin/train-models', headers=headers, json={})

    assert response.status_code == 202
    assert calls and calls[0][0][0] == 'python'


@pytest.mark.case('API-16', 'Admin เรียก Batch Train แบบ Synchronous')
def test_api_16_admin_sync_train(app, client, monkeypatch):
    from app.routers import admin as admin_router

    _admin_id, headers = create_admin(app)
    monkeypatch.setattr(
        admin_router.predictor_service,
        'run_batch_train_all',
        lambda: {'trained': 3, 'failed': 0},
    )

    response = client.post('/api/admin/train-models/sync', headers=headers, json={})

    assert response.status_code == 200
    assert response.get_json()['data']['trained'] == 3
