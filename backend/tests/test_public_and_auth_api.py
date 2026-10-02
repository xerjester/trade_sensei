"""One automated test function per documented Guest/Auth test case."""
from datetime import date, datetime

import pytest

from app.core.database import db
from app.models.schema import HistoricalPrice, News, Stock, User


def seed_market_data(app):
    """Create deterministic D2–D4 records and return the stock symbol."""
    with app.app_context():
        stock = Stock(symbol='PTT.BK', company_name='PTT', category='Energy')
        db.session.add(stock)
        db.session.flush()
        db.session.add(HistoricalPrice(
            stock_id=stock.stock_id,
            date=date(2026, 1, 2),
            open_price=30,
            high_price=31,
            low_price=29,
            close_price=30.5,
            volume=1200,
        ))
        db.session.add(News(
            stock_id=stock.stock_id,
            title='PTT update',
            url_link='https://example.test/ptt',
            published_date=datetime(2026, 1, 2, 10, 0),
        ))
        db.session.commit()
    return 'PTT.BK'


@pytest.mark.case('TC-01', 'API ตอบสนองและส่ง Security Headers',
                  'HSTS ถูกทดสอบแยกใน production เพราะ test app เปิด debug mode')
def test_tc_01_health_and_security_headers(client):
    response = client.get('/')

    assert response.status_code == 200
    assert response.get_json()['status'] == 'success'
    assert response.headers['X-Content-Type-Options'] == 'nosniff'
    assert response.headers['X-Frame-Options'] == 'DENY'


@pytest.mark.case('TC-02', 'ปฏิเสธ API write ที่ไม่ใช่ JSON')
def test_tc_02_reject_non_json_write(client):
    response = client.post('/api/auth/login', data='email=a@example.com')

    assert response.status_code == 415
    assert response.get_json()['status'] == 'error'


@pytest.mark.case('TC-03A', 'สมัครสมาชิกและ normalize อีเมล',
                  'ปิด rate limit ใน test environment เพื่อให้ผลไม่ขึ้นกับลำดับการรัน')
def test_tc_03a_register_member(app, client):
    response = client.post('/api/auth/register', json={
        'first_name': 'Ada',
        'last_name': 'Lovelace',
        'email': 'ADA@Example.com',
        'password': 'SecurePass1',
    })

    assert response.status_code == 201
    assert response.get_json()['user']['email'] == 'ada@example.com'
    assert response.get_json()['user']['role'] == 'member'
    with app.app_context():
        assert User.query.filter_by(email='ada@example.com').count() == 1


@pytest.mark.case('TC-03B', 'เข้าสู่ระบบและอ่านข้อมูลผู้ใช้ด้วย JWT')
def test_tc_03b_login_and_current_user(client):
    payload = {
        'first_name': 'Ada',
        'email': 'ada@example.com',
        'password': 'SecurePass1',
    }
    assert client.post('/api/auth/register', json=payload).status_code == 201

    login = client.post('/api/auth/login', json={
        'email': payload['email'], 'password': payload['password'],
    })
    assert login.status_code == 200
    token = login.get_json()['access_token']

    me = client.get('/api/auth/me', headers={'Authorization': f'Bearer {token}'})
    assert me.status_code == 200
    assert me.get_json()['user']['email'] == payload['email']


@pytest.mark.case('TC-04A', 'ปฏิเสธรหัสผ่านที่ไม่ผ่าน Password Policy')
def test_tc_04a_reject_weak_password(client):
    response = client.post('/api/auth/register', json={
        'first_name': 'Weak',
        'email': 'weak@example.com',
        'password': 'password',
    })

    assert response.status_code == 400
    assert response.get_json()['status'] == 'error'


@pytest.mark.case('TC-04B', 'ปฏิเสธการสมัครด้วยอีเมลซ้ำ')
def test_tc_04b_reject_duplicate_email(client):
    payload = {
        'first_name': 'Valid',
        'email': 'valid@example.com',
        'password': 'SecurePass1',
    }
    assert client.post('/api/auth/register', json=payload).status_code == 201

    duplicate = client.post('/api/auth/register', json=payload)
    assert duplicate.status_code == 400
    assert duplicate.get_json()['status'] == 'error'


@pytest.mark.case('TC-06A', 'Guest อ่านรายการหุ้นจาก D2',
                  'ใช้ fixture ในฐานข้อมูล ไม่ได้ทดสอบข้อมูลสดจาก Yahoo Finance')
def test_tc_06a_list_stocks(app, client):
    seed_market_data(app)

    response = client.get('/api/stocks')
    assert response.status_code == 200
    assert response.get_json()['data'][0]['symbol'] == 'PTT.BK'


@pytest.mark.case('TC-06B', 'Guest อ่านข้อมูลราคา OHLCV จาก D3',
                  'ตรวจ API mapping ด้วยราคาคงที่ ไม่ได้ตรวจความถูกต้องของตลาดจริง')
def test_tc_06b_read_ohlcv(app, client):
    seed_market_data(app)

    response = client.get('/api/stock-data/ptt.bk')
    assert response.status_code == 200
    assert response.get_json()['data']['closes'] == [30.5]


@pytest.mark.case('TC-06C', 'Guest อ่านข่าวหุ้นจาก D4',
                  'ลิงก์ข่าวเป็น fixture และไม่มี HTTP request ไปยังเว็บไซต์ต้นทาง')
def test_tc_06c_read_stock_news(app, client):
    seed_market_data(app)

    response = client.get('/api/news/PTT.BK')
    assert response.status_code == 200
    assert response.get_json()['data'][0]['title'] == 'PTT update'


@pytest.mark.case('TC-07A', 'ปฏิเสธ Symbol ผิดรูปแบบใน Price API')
def test_tc_07a_reject_invalid_price_symbol(client):
    response = client.get('/api/stock-data/bad%20symbol')

    assert response.status_code == 400
    assert response.get_json()['status'] == 'error'


@pytest.mark.case('TC-07B', 'ปฏิเสธ Symbol ผิดรูปแบบใน News API')
def test_tc_07b_reject_invalid_news_symbol(client):
    response = client.get('/api/news/<script>')

    assert response.status_code == 400
    assert response.get_json()['status'] == 'error'
