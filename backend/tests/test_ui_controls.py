"""UI control contracts: every project button is wired to its intended outcome.

These tests are deterministic and inspect the shipped HTML/JavaScript bundle.
They complement browser E2E tests by catching missing IDs, detached handlers,
renamed endpoints, and buttons with no accessible name.
"""
from pathlib import Path

import pytest
from bs4 import BeautifulSoup


FRONTEND_ROOT = Path(__file__).resolve().parents[2] / 'frontend'


def load_page(page_name):
    html = (FRONTEND_ROOT / page_name).read_text(encoding='utf-8')
    soup = BeautifulSoup(html, 'html.parser')
    scripts = []
    for script in soup.find_all('script', src=True):
        path = FRONTEND_ROOT / script['src']
        if path.exists():
            scripts.append(path.read_text(encoding='utf-8'))
    return soup, '\n'.join(scripts)


def ui_case(case_id, title, page, selector, wiring, expected_tokens, caution=''):
    return pytest.param(
        page, selector, wiring, expected_tokens,
        id=f'{case_id}-{page}-{selector}',
        marks=pytest.mark.case(case_id, title, caution),
    )


UI_CASES = [
    ui_case('UI-01', 'ปุ่มเมนูหน้า Dashboard เปิด/ปิด Navigation', 'index.html', '#nav-toggle',
            'listener:nav-toggle:click', ['nav-open', 'aria-expanded']),
    ui_case('UI-02', 'ปุ่มเข้าสู่ระบบนำไปหน้า Login', 'index.html', '#login-btn',
            'onclick:handleAuthButton()', ['login.html']),
    ui_case('UI-03', 'ปุ่มสมัครฟรีนำไปหน้า Register', 'index.html', '#register-btn',
            'onclick:goToRegister()', ['register.html']),
    ui_case('UI-04', 'ปุ่มสำรวจตลาดเลื่อนไป Dashboard', 'index.html',
            'button[onclick="scrollToDashboard()"]', 'onclick:scrollToDashboard()', ['app-dashboard']),
    ui_case('UI-05', 'ปุ่ม Forecast เปิด/ปิดผลทำนาย 7 วัน', 'index.html', '#prediction-btn',
            'onclick:togglePrediction()', ['/api/predict/', 'isPredictionEnabled']),
    ui_case('UI-06', 'ปุ่ม Backtest เปิด Time Machine', 'index.html', '#time-machine-btn',
            'onclick:toggleTimeMachine()', ['backtest-modal']),
    ui_case('UI-07', 'ปุ่ม Ask Sensei เปิด Copilot', 'index.html', '#copilot-btn',
            'onclick:openCopilotModal()', ['copilot-modal']),
    ui_case('UI-08A', 'ปุ่มช่วงกราฟ 1D เปลี่ยนข้อมูลเป็น 1 วัน', 'index.html', '[data-range="1D"]',
            "onclick:setChartRange('1D')", ['currentChartRange']),
    ui_case('UI-08B', 'ปุ่มช่วงกราฟ 7D เปลี่ยนข้อมูลเป็น 7 วัน', 'index.html', '[data-range="7D"]',
            "onclick:setChartRange('7D')", ['currentChartRange']),
    ui_case('UI-08C', 'ปุ่มช่วงกราฟ 1M เปลี่ยนข้อมูลเป็น 1 เดือน', 'index.html', '[data-range="1M"]',
            "onclick:setChartRange('1M')", ['currentChartRange']),
    ui_case('UI-08D', 'ปุ่มช่วงกราฟ 6M เปลี่ยนข้อมูลเป็น 6 เดือน', 'index.html', '[data-range="6M"]',
            "onclick:setChartRange('6M')", ['currentChartRange']),
    ui_case('UI-08E', 'ปุ่มช่วงกราฟ 1Y เปลี่ยนข้อมูลเป็น 1 ปี', 'index.html', '[data-range="1Y"]',
            "onclick:setChartRange('1Y')", ['currentChartRange']),
    ui_case('UI-08F', 'ปุ่มช่วงกราฟ 2Y เปลี่ยนข้อมูลเป็น 2 ปี', 'index.html', '[data-range="2Y"]',
            "onclick:setChartRange('2Y')", ['currentChartRange']),
    ui_case('UI-09', 'ปุ่มสมัครใน Locked Analysis เปิดหน้า Register', 'index.html',
            '.locked-overlay button', "onclick:location.href='register.html'", ['register.html']),
    ui_case('UI-10', 'ปุ่มลบประวัติ Copilot เรียก DELETE History', 'index.html',
            '.clear-history-btn', 'onclick:clearCopilotHistory()', ["method: 'DELETE'", '/api/copilot/history']),
    ui_case('UI-11', 'ปุ่มปิด Copilot ซ่อน Modal', 'index.html',
            '#copilot-modal .modal-close', 'onclick:closeCopilotModal()', ['copilot-modal']),
    ui_case('UI-12', 'ปุ่มส่งข้อความส่งคำถามเข้า Copilot API', 'index.html', '#chat-send-btn',
            'onclick:sendCopilotMessage()', ["method: 'POST'", '/api/copilot/chat']),
    ui_case('UI-13', 'ปุ่มปิด Change Password ซ่อน Modal', 'index.html',
            '#password-modal .modal-close', 'onclick:closePasswordModal()', ['password-modal']),
    ui_case('UI-14', 'ปุ่มบันทึกรหัสผ่านเรียก Change Password API', 'index.html',
            '#password-modal .btn-primary', 'onclick:submitPasswordChange()', ['/api/auth/change-password']),
    ui_case('UI-15', 'ปุ่มยกเลิก Change Password ซ่อน Modal', 'index.html',
            '#password-modal .btn-ghost', 'onclick:closePasswordModal()', ['password-modal']),
    ui_case('UI-16', 'ปุ่มกากบาท Time Machine ซ่อน Modal', 'index.html',
            '#backtest-modal .modal-close', 'onclick:closeBacktestModal()', ['backtest-modal']),
    ui_case('UI-17', 'ปุ่มเริ่มจำลองเรียก Backtest API', 'index.html',
            '#backtest-modal .btn-primary', 'onclick:runBacktest()', ['/api/backtest/']),
    ui_case('UI-18', 'ปุ่มปิด Time Machine ซ่อน Modal', 'index.html',
            '#backtest-modal .btn-ghost', 'onclick:closeBacktestModal()', ['backtest-modal']),
    ui_case('UI-19', 'ปุ่มเมนูหน้า Login เปิด/ปิด Navigation', 'login.html', '#nav-toggle',
            'listener:nav-toggle:click', ['nav-open']),
    ui_case('UI-20', 'ปุ่ม Login ส่งข้อมูลและบันทึก Session', 'login.html', '#login-submit',
            'submit:login-form', ['/api/auth/login', 'setAuthSession', 'redirectByRole']),
    ui_case('UI-21', 'ปุ่มลืมรหัสผ่านเปิด OTP Modal', 'login.html', '#forgot-password-btn',
            'listener:forgot-password-btn:click', ['forgot-password-modal', 'reset-email']),
    ui_case('UI-22', 'ปุ่มปิด Forgot Password ซ่อน Modal', 'login.html', '#forgot-password-close',
            'listener:forgot-password-close:click', ['closeForgotPasswordModal']),
    ui_case('UI-23', 'ปุ่มส่ง OTP เรียก Forgot Password API', 'login.html', '#request-otp-btn',
            'submit:request-otp-form', ['/api/auth/forgot-password', 'reset-password-form']),
    ui_case('UI-24', 'ปุ่มตั้งรหัสใหม่เรียก Reset Password API', 'login.html', '#reset-password-btn',
            'submit:reset-password-form', ['/api/auth/reset-password']),
    ui_case('UI-25', 'ปุ่มเมนูหน้า Register เปิด/ปิด Navigation', 'register.html', '#nav-toggle',
            'listener:nav-toggle:click', ['nav-open']),
    ui_case('UI-26', 'ปุ่มสมัครสมาชิกส่งข้อมูลและบันทึก Session', 'register.html', '#register-submit',
            'submit:register-form', ['/api/auth/register', 'setAuthSession', 'index.html']),
    ui_case('UI-27', 'ปุ่มเมนูหน้า Admin เปิด/ปิด Navigation', 'admin.html', '#nav-toggle',
            'listener:nav-toggle:click', ['nav-open']),
    ui_case('UI-28', 'ปุ่มเปลี่ยนรหัสผ่าน Admin เปิด Modal', 'admin.html',
            'button[onclick="openPasswordModal()"]', 'onclick:openPasswordModal()', ['password-modal']),
    ui_case('UI-29', 'ปุ่มออกจากระบบ Admin ล้าง Session', 'admin.html',
            'button[onclick="logoutAdmin()"]', 'onclick:logoutAdmin()', ['removeItem', 'login.html']),
    ui_case('UI-30', 'ปุ่มรีเฟรช Log โหลด D7 ใหม่', 'admin.html',
            'button[onclick="loadLogs()"]', 'onclick:loadLogs()', ['/api/admin/logs']),
    ui_case('UI-31', 'ปุ่มเพิ่มหุ้นส่ง Master Data', 'admin.html',
            'button[onclick="addStock()"]', 'onclick:addStock()', ["method: 'POST'", '/api/admin/stocks']),
    ui_case('UI-32', 'ปุ่มดึงข้อมูลตลาดเริ่ม Scraper', 'admin.html',
            "button[onclick=\"runTask('run-scraper')\"]", "onclick:runTask('run-scraper')", ['/api/admin/']),
    ui_case('UI-33', 'ปุ่มเทรน Prophet เริ่ม Batch Train', 'admin.html',
            'button[onclick="trainModels()"]', 'onclick:trainModels()', ['train-models']),
    ui_case('UI-34', 'ปุ่มรีเฟรชรายชื่อโหลด Users ใหม่', 'admin.html',
            'button[onclick="loadUsers()"]', 'onclick:loadUsers()', ['/api/admin/users']),
    ui_case('UI-35', 'ปุ่มปิด User Edit ซ่อน Modal', 'admin.html',
            '#user-edit-modal .modal-close', 'onclick:closeUserEditModal()', ['user-edit-modal']),
    ui_case('UI-36', 'ปุ่มบันทึก User Edit เรียก Update API', 'admin.html',
            '#user-edit-modal .btn-primary', 'onclick:saveUserEdit()', ["method: 'PUT'", '/api/admin/users/']),
    ui_case('UI-37', 'ปุ่มยกเลิก User Edit ซ่อน Modal', 'admin.html',
            '#user-edit-modal .btn-ghost', 'onclick:closeUserEditModal()', ['user-edit-modal']),
    ui_case('UI-38', 'ปุ่มปิด Password Admin ซ่อน Modal', 'admin.html',
            '#password-modal .modal-close', 'onclick:closePasswordModal()', ['password-modal']),
    ui_case('UI-39', 'ปุ่มบันทึกรหัสผ่าน Admin เรียก Change Password API', 'admin.html',
            '#password-modal .btn-primary', 'onclick:submitPasswordChange()', ['/api/auth/change-password']),
    ui_case('UI-40', 'ปุ่มยกเลิกรหัสผ่าน Admin ซ่อน Modal', 'admin.html',
            '#password-modal .btn-ghost', 'onclick:closePasswordModal()', ['password-modal']),
]


@pytest.mark.parametrize('page_name,selector,wiring,expected_tokens', UI_CASES)
def test_ui_control_contract(page_name, selector, wiring, expected_tokens):
    soup, javascript = load_page(page_name)
    elements = soup.select(selector)
    assert elements, f'ไม่พบ control {selector} ใน {page_name}'
    element = elements[0]

    wiring_type, wiring_value = wiring.split(':', 1)
    if wiring_type == 'onclick':
        assert element.get('onclick') == wiring_value
    elif wiring_type == 'submit':
        form = element.find_parent('form')
        assert form is not None and form.get('id') == wiring_value
        assert f"getElementById('{wiring_value}').addEventListener('submit'" in javascript
    elif wiring_type == 'listener':
        element_id, event_name = wiring_value.split(':', 1)
        assert element.get('id') == element_id
        assert f"getElementById('{element_id}')" in javascript
        assert f"addEventListener('{event_name}'" in javascript
    else:
        raise AssertionError(f'Unknown wiring type: {wiring_type}')

    for token in expected_tokens:
        assert token in javascript or token in str(element)


@pytest.mark.case('UI-41', 'ปุ่มทุกตัวมี type และชื่อที่อ่านได้')
@pytest.mark.parametrize('page_name', ['index.html', 'login.html', 'register.html', 'admin.html'])
def test_ui_41_all_buttons_are_accessible(page_name):
    soup, _javascript = load_page(page_name)

    for button in soup.find_all('button'):
        assert button.get('type') in {'button', 'submit'}
        assert button.get_text(' ', strip=True) or button.get('aria-label')


@pytest.mark.case('UI-42', 'ปุ่มลบ/แก้ไข Dynamic Table ผูก Event โดยไม่ฝังข้อมูลใน onclick',
                  'Browser E2E ยังควรรันทวน confirm dialog ใน staging')
def test_ui_42_dynamic_admin_buttons_avoid_inline_user_data():
    _soup, javascript = load_page('admin.html')

    assert 'data-action="delete-stock"' in javascript
    assert 'data-action="edit-user"' in javascript
    assert 'data-action="delete-user"' in javascript
    assert "addEventListener(\n            'click'" in javascript
    assert 'onclick="deleteUser(' not in javascript


@pytest.mark.case('UI-43', 'ข้อมูลผู้ใช้ หุ้น และ Log ถูก Encode ก่อนแสดงผล',
                  'Defense-in-depth ฝั่ง backend ปฏิเสธ markup ในชื่อผู้ใช้เพิ่มเติมแล้ว')
def test_ui_43_admin_output_encoding_present():
    _soup, javascript = load_page('admin.html')

    assert 'function escapeAdminHtml' in javascript
    assert 'line.textContent = String(message' in javascript
    assert 'logWin.innerHTML +=' not in javascript
    assert 'escapeAdminHtml(user.email)' in javascript
    assert 'escapeAdminHtml(stock.category' in javascript


@pytest.mark.case('UI-44', 'ลิงก์ข่าวอนุญาตเฉพาะ HTTP/HTTPS เพื่อกัน javascript URL')
def test_ui_44_news_links_reject_dangerous_protocols():
    _soup, javascript = load_page('index.html')

    assert 'function getSafeExternalUrl' in javascript
    assert "['http:', 'https:'].includes(url.protocol)" in javascript
    assert 'link.href = safeNewsUrl' in javascript
