// แสดงข้อความ error บนฟอร์มสมัครสมาชิก
function showRegisterError(message) {
    const errorEl = document.getElementById('register-error');
    errorEl.textContent = message;
    errorEl.hidden = !message;
}

// ตรวจสอบข้อมูลและส่งสมัครสมาชิกใหม่
document.getElementById('register-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    showRegisterError('');

    const first_name = document.getElementById('first_name').value.trim();
    const last_name = document.getElementById('last_name').value.trim();
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;
    const confirm_password = document.getElementById('confirm_password').value;
    const submitBtn = document.getElementById('register-submit');

    // เช็กว่ารหัสผ่าน 2 ช่องตรงกันไหม
    if (password !== confirm_password) {
        showRegisterError('รหัสผ่านไม่ตรงกัน');
        return;
    }

    submitBtn.disabled = true;
    submitBtn.textContent = 'กำลังสมัคร...';

    try {
        const result = await apiJson(`${API_BASE}/api/auth/register`, {
            method: 'POST',
            body: JSON.stringify({ first_name, last_name, email, password }),
        });

        if (result.status !== 'success') {
            showRegisterError(result.message || 'สมัครสมาชิกไม่สำเร็จ');
            return;
        }

        // สมัครสำเร็จ เก็บ session แล้วพาไปหน้าแรก
        setAuthSession(result.access_token, result.user);
        sessionStorage.setItem('tradesensei_just_logged_in', '1');
        window.location.href = 'index.html';
    } catch (error) {
        console.error('Register failed:', error);
        showRegisterError('ไม่สามารถเชื่อมต่อเซิร์ฟเวอร์ Backend ได้');
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'สมัครสมาชิก';
    }
});

// ถ้าล็อกอินอยู่แล้ว ให้เด้งไปหน้าแรกตามสิทธิ์ทันที
(function redirectIfAuthenticated() {
    const token = localStorage.getItem('tradesensei_token');
    const user = getStoredUser();
    if (token && user) redirectByRole(user);
})();

// ผูกปุ่มเข้าสู่ระบบด้วยบัญชี Google
document.addEventListener('DOMContentLoaded', () => {
    initGoogleSignIn('google-signin-btn');
});
