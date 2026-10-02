function showLoginError(message) {
    const errorEl = document.getElementById('login-error');
    errorEl.textContent = message;
    errorEl.hidden = !message;
}

function showResetMessage(message, isError = true) {
    const messageEl = document.getElementById('reset-password-message');
    messageEl.textContent = message;
    messageEl.hidden = !message;
    messageEl.classList.toggle('auth-success', !isError);
}

function resetForgotPasswordSteps() {
    const titleEl = document.getElementById('forgot-password-title');
    const subtitleEl = document.getElementById('forgot-password-subtitle');
    const reqForm = document.getElementById('request-otp-form');
    const verifyForm = document.getElementById('verify-otp-form');
    const resetForm = document.getElementById('reset-password-form');
    const otpInput = document.getElementById('reset-otp');
    const newPassInput = document.getElementById('reset-new-password');
    const confirmPassInput = document.getElementById('reset-confirm-password');

    if (titleEl) titleEl.textContent = 'รีเซ็ตรหัสผ่าน';
    if (subtitleEl) subtitleEl.textContent = 'กรอกอีเมลเพื่อรับรหัส OTP ทางอีเมล รหัสมีอายุ 10 นาที';
    if (reqForm) reqForm.hidden = false;
    if (verifyForm) verifyForm.hidden = true;
    if (resetForm) resetForm.hidden = true;
    if (otpInput) otpInput.value = '';
    if (newPassInput) newPassInput.value = '';
    if (confirmPassInput) confirmPassInput.value = '';
    showResetMessage('');
}

function closeForgotPasswordModal() {
    document.getElementById('forgot-password-modal').hidden = true;
    resetForgotPasswordSteps();
}

document.getElementById('forgot-password-btn').addEventListener('click', () => {
    resetForgotPasswordSteps();
    const resetEmail = document.getElementById('reset-email');
    resetEmail.value = document.getElementById('email').value.trim();
    document.getElementById('forgot-password-modal').hidden = false;
    resetEmail.focus();
});

document.getElementById('forgot-password-close').addEventListener('click', closeForgotPasswordModal);

// ขั้นตอนที่ 1: ตรวจสอบอีเมลในระบบ และส่ง OTP
document.getElementById('request-otp-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    showResetMessage('');
    const email = document.getElementById('reset-email').value.trim();
    const button = document.getElementById('request-otp-btn');
    button.disabled = true;
    button.textContent = 'กำลังตรวจสอบ...';

    // ซ่อนฟอร์ม reset-password-form ไว้
    document.getElementById('reset-password-form').hidden = true;

    try {
        const result = await apiJson(`${API_BASE}/api/auth/forgot-password`, {
            method: 'POST',
            body: JSON.stringify({ email }),
        });
        if (result.status !== 'success') {
            showResetMessage(result.message || 'ไม่พบอีเมลนี้ในระบบ');
            return;
        }

        // หากมีอีเมลในระบบ และส่ง OTP สำเร็จ -> เด้งมาหน้ากรอก OTP 6 ตัว (ขั้นตอนที่ 2)
        document.getElementById('forgot-password-title').textContent = 'กรอกรหัส OTP';
        document.getElementById('forgot-password-subtitle').textContent = `รหัส OTP 6 หลักถูกส่งไปยัง ${email} แล้ว (มีอายุ 10 นาที)`;
        document.getElementById('request-otp-form').hidden = true;
        document.getElementById('verify-otp-form').hidden = false;
        document.getElementById('reset-password-form').hidden = true;
        showResetMessage('ส่งรหัส OTP แล้ว กรุณาตรวจสอบกล่องจดหมายของคุณ', false);
        const otpInput = document.getElementById('reset-otp');
        otpInput.value = '';
        otpInput.focus();
    } catch {
        showResetMessage('ไม่สามารถเชื่อมต่อเซิร์ฟเวอร์ได้');
    } finally {
        button.disabled = false;
        button.textContent = 'ส่งรหัส OTP';
    }
});

// ขั้นตอนที่ 2: ตรวจสอบรหัส OTP 6 ตัว
const verifyOtpForm = document.getElementById('verify-otp-form');
if (verifyOtpForm) {
    verifyOtpForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        showResetMessage('');
        const email = document.getElementById('reset-email').value.trim();
        const otp = document.getElementById('reset-otp').value.trim();
        const button = document.getElementById('verify-otp-btn');

        if (!otp || otp.length !== 6 || !/^\d{6}$/.test(otp)) {
            showResetMessage('กรุณากรอกรหัส OTP เป็นตัวเลข 6 หลักให้ครบถ้วน');
            return;
        }

        button.disabled = true;
        button.textContent = 'กำลังตรวจสอบ OTP...';

        try {
            const result = await apiJson(`${API_BASE}/api/auth/verify-otp`, {
                method: 'POST',
                body: JSON.stringify({ email, otp }),
            });

            if (result.status !== 'success') {
                showResetMessage(result.message || 'รหัส OTP ไม่ถูกต้องหรือหมดอายุ');
                return;
            }

            // ถ้ากรอก OTP ถูกต้อง -> เด้งไปหน้าตั้งรหัสผ่านใหม่ (ขั้นตอนที่ 3)
            document.getElementById('forgot-password-title').textContent = 'ตั้งรหัสผ่านใหม่';
            document.getElementById('forgot-password-subtitle').textContent = 'กำหนดรหัสผ่านใหม่สำหรับบัญชีของคุณ';
            document.getElementById('verify-otp-form').hidden = true;
            document.getElementById('reset-password-form').hidden = false;
            showResetMessage('ยืนยัน OTP ถูกต้อง กรุณาตั้งรหัสผ่านใหม่', false);
            document.getElementById('reset-new-password').focus();
        } catch {
            showResetMessage('ไม่สามารถเชื่อมต่อเซิร์ฟเวอร์ได้');
        } finally {
            button.disabled = false;
            button.textContent = 'ยืนยันรหัส OTP';
        }
    });
}

// ปุ่มย้อนกลับไปเปลี่ยนอีเมล
const changeEmailBtn = document.getElementById('change-email-btn');
if (changeEmailBtn) {
    changeEmailBtn.addEventListener('click', () => {
        resetForgotPasswordSteps();
        document.getElementById('reset-email').focus();
    });
}

// ปุ่มขอรหัสใหม่อีกครั้ง
const resendOtpBtn = document.getElementById('resend-otp-btn');
if (resendOtpBtn) {
    resendOtpBtn.addEventListener('click', () => {
        document.getElementById('request-otp-form').dispatchEvent(new Event('submit'));
    });
}

// ขั้นตอนที่ 3: ตั้งรหัสผ่านใหม่ (เมื่อ OTP ถูกต้อง)
document.getElementById('reset-password-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    showResetMessage('');
    const email = document.getElementById('reset-email').value.trim();
    const otp = document.getElementById('reset-otp').value.trim();
    const password = document.getElementById('reset-new-password').value;
    const confirmPassword = document.getElementById('reset-confirm-password').value;

    if (password !== confirmPassword) {
        showResetMessage('รหัสผ่านใหม่ไม่ตรงกัน กรุณาตรวจสอบอีกครั้ง');
        return;
    }
    if (password.length < 8 || !/\d/.test(password)) {
        showResetMessage('รหัสผ่านต้องมีอย่างน้อย 8 ตัวอักษรและมีตัวเลขอย่างน้อย 1 ตัว');
        return;
    }

    const button = document.getElementById('reset-password-btn');
    button.disabled = true;
    button.textContent = 'กำลังบันทึก...';
    try {
        const result = await apiJson(`${API_BASE}/api/auth/reset-password`, {
            method: 'POST',
            body: JSON.stringify({
                email,
                otp,
                new_password: password,
            }),
        });
        if (result.status !== 'success') {
            showResetMessage(result.message || 'ไม่สามารถตั้งรหัสผ่านใหม่ได้');
            return;
        }
        showResetMessage('ตั้งรหัสผ่านใหม่สำเร็จ กำลังพาไปหน้าเข้าสู่ระบบ...', false);
        document.getElementById('email').value = email;
        setTimeout(closeForgotPasswordModal, 1500);
    } catch {
        showResetMessage('ไม่สามารถเชื่อมต่อเซิร์ฟเวอร์ได้');
    } finally {
        button.disabled = false;
        button.textContent = 'บันทึกรหัสผ่านใหม่';
    }
});

document.getElementById('login-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    showLoginError('');

    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;
    const submitBtn = document.getElementById('login-submit');

    submitBtn.disabled = true;
    submitBtn.textContent = 'กำลังตรวจสอบ...';

    try {
        const result = await apiJson(`${API_BASE}/api/auth/login`, {
            method: 'POST',
            body: JSON.stringify({ email, password }),
        });

        if (result.status !== 'success') {
            showLoginError(result.message || 'เข้าสู่ระบบไม่สำเร็จ');
            return;
        }

        setAuthSession(result.access_token, result.user);
        if (result.user.role === 'member') {
            sessionStorage.setItem('tradesensei_just_logged_in', '1');
        }
        redirectByRole(result.user);
    } catch (error) {
        console.error('Login failed:', error);
        showLoginError('ไม่สามารถเชื่อมต่อเซิร์ฟเวอร์ Backend ได้');
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'เข้าสู่ระบบ';
    }
});

(function redirectIfAuthenticated() {
    const token = localStorage.getItem('tradesensei_token');
    const user = getStoredUser();
    if (token && user) redirectByRole(user);
})();

document.addEventListener('DOMContentLoaded', () => {
    initGoogleSignIn('google-signin-btn');
});
