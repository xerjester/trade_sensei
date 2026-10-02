"""One automated test function per documented Member/Admin test case."""
import pytest

from app.core.database import db
from app.models.schema import ChatHistory, Stock, SystemLog

from conftest import auth_header, create_user


def seed_two_chat_owners(app):
    """Create deterministic D6 records owned by different users."""
    first_id = create_user(app, email='first@example.com')
    second_id = create_user(app, email='second@example.com')
    with app.app_context():
        db.session.add_all([
            ChatHistory(
                user_id=first_id,
                message='first question',
                response_text='first answer',
                provider='test',
            ),
            ChatHistory(
                user_id=second_id,
                message='second question',
                response_text='second answer',
                provider='test',
            ),
        ])
        db.session.commit()
    return first_id, second_id


@pytest.mark.case('TC-05A', 'ปฏิเสธการอ่านข้อมูลผู้ใช้เมื่อไม่มี JWT')
def test_tc_05a_profile_requires_jwt(client):
    response = client.get('/api/auth/me')

    assert response.status_code == 401
    assert response.get_json()['status'] == 'error'


@pytest.mark.case('TC-05B', 'ปฏิเสธการอ่าน Chat History เมื่อไม่มี JWT')
def test_tc_05b_chat_history_requires_jwt(client):
    response = client.get('/api/copilot/history')

    assert response.status_code == 401
    assert response.get_json()['status'] == 'error'


@pytest.mark.case('TC-08', 'สมาชิกเห็นเฉพาะ Chat History ของตนเอง',
                  'ทดสอบ ownership ใน API/DB แต่ไม่ส่งคำถามจริงไปยัง Gemini')
def test_tc_08_chat_history_isolation(app, client):
    first_id, _second_id = seed_two_chat_owners(app)

    response = client.get(
        '/api/copilot/history',
        headers=auth_header(app, first_id, email='first@example.com'),
    )

    assert response.status_code == 200
    assert [row['message'] for row in response.get_json()['data']] == ['first question']


@pytest.mark.case('TC-09', 'สมาชิกลบเฉพาะ Chat History ของตนเอง')
def test_tc_09_clear_only_own_chat_history(app, client):
    first_id, second_id = seed_two_chat_owners(app)

    response = client.delete(
        '/api/copilot/history',
        headers=auth_header(app, first_id, email='first@example.com'),
    )

    assert response.status_code == 200
    assert response.get_json()['deleted'] == 1
    with app.app_context():
        assert ChatHistory.query.filter_by(user_id=first_id).count() == 0
        assert ChatHistory.query.filter_by(user_id=second_id).count() == 1
        assert SystemLog.query.filter_by(
            user_id=first_id,
            action_type='USER_COPILOT_HISTORY_CLEARED',
        ).count() == 1


@pytest.mark.case('TC-11', 'Member ไม่สามารถเรียก Admin API')
def test_tc_11_member_cannot_use_admin_routes(app, client):
    member_id = create_user(app)

    response = client.get('/api/admin/logs', headers=auth_header(app, member_id))

    assert response.status_code == 403
    assert response.get_json()['status'] == 'error'


@pytest.mark.case('TC-12A', 'Admin เพิ่มหุ้นและ normalize Symbol')
def test_tc_12a_admin_adds_normalized_stock(app, client):
    admin_id = create_user(app, email='admin-test@example.com', role='admin')
    headers = auth_header(app, admin_id, role='admin', email='admin-test@example.com')

    response = client.post('/api/admin/stocks', headers=headers, json={
        'symbol': 'aapl',
        'company_name': 'Apple Inc.',
        'category': 'Technology',
    })

    assert response.status_code == 201
    assert response.get_json()['message'].startswith('เพิ่มหุ้น AAPL')
    with app.app_context():
        assert Stock.query.filter_by(symbol='AAPL').count() == 1


@pytest.mark.case('TC-12B', 'Admin ไม่สามารถเพิ่มหุ้น Symbol ซ้ำ')
def test_tc_12b_admin_cannot_add_duplicate_stock(app, client):
    admin_id = create_user(app, email='admin-test@example.com', role='admin')
    headers = auth_header(app, admin_id, role='admin', email='admin-test@example.com')
    payload = {
        'symbol': 'AAPL',
        'company_name': 'Apple Inc.',
        'category': 'Technology',
    }
    assert client.post('/api/admin/stocks', headers=headers, json=payload).status_code == 201

    response = client.post('/api/admin/stocks', headers=headers, json=payload)
    assert response.status_code == 400
    assert response.get_json()['status'] == 'error'


@pytest.mark.case('TC-13', 'Admin กรอง System Log ตาม action และ limit')
def test_tc_13_admin_filters_system_logs(app, client):
    admin_id = create_user(app, email='admin-test@example.com', role='admin')
    headers = auth_header(app, admin_id, role='admin', email='admin-test@example.com')
    with app.app_context():
        db.session.add_all([
            SystemLog(user_id=admin_id, action_type='TEST_A', description='first'),
            SystemLog(user_id=admin_id, action_type='TEST_B', description='second'),
        ])
        db.session.commit()

    response = client.get(
        '/api/admin/logs?action_type=TEST_A&limit=1',
        headers=headers,
    )

    assert response.status_code == 200
    assert len(response.get_json()['data']) == 1
    assert response.get_json()['data'][0]['action_type'] == 'TEST_A'


@pytest.mark.case('TC-10A', 'ปฏิเสธข้อมูล Backtest ที่แปลงค่าไม่ได้',
                  'ยังต้องมี integration test แยกสำหรับการคำนวณผลตอบแทนจริง')
def test_tc_10a_reject_invalid_backtest_values(app, client):
    member_id = create_user(app)

    response = client.post(
        '/api/backtest/AAPL',
        headers=auth_header(app, member_id),
        json={'months': 'invalid', 'initial_amount': 1000},
    )

    assert response.status_code == 400
    assert response.get_json()['status'] == 'error'


@pytest.mark.case('TC-10B', 'ปฏิเสธ Symbol ผิดรูปแบบใน Copilot')
def test_tc_10b_reject_invalid_copilot_symbol(app, client):
    member_id = create_user(app)

    response = client.post(
        '/api/copilot/chat',
        headers=auth_header(app, member_id),
        json={'symbol': 'bad symbol!', 'message': 'Hello'},
    )

    assert response.status_code == 400
    assert response.get_json()['status'] == 'error'


@pytest.mark.case('TC-10C', 'ปฏิเสธคำถาม Copilot ที่ยาวเกิน 1,000 ตัวอักษร',
                  'การ grounded response จาก Gemini ต้องทดสอบแยกด้วย controlled fixture')
def test_tc_10c_reject_oversized_copilot_message(app, client):
    member_id = create_user(app)

    response = client.post(
        '/api/copilot/chat',
        headers=auth_header(app, member_id),
        json={'symbol': 'AAPL', 'message': 'x' * 1001},
    )

    assert response.status_code == 400
    assert response.get_json()['status'] == 'error'
