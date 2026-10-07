// =============================================================================
// TradeSensei — Authentication & Shared UI Interaction Utilities
// ระบบจัดการการยืนยันตัวตน Session และลูกเล่นปฏิสัมพันธ์หน้าจอส่วนกลาง
// =============================================================================

const API_BASE = 'https://tradesensei-backend.onrender.com';

const AUTH_TOKEN_KEY = 'tradesensei_token';
const AUTH_USER_KEY = 'tradesensei_user';

/**
 * บันทึก Session การเข้าสู่ระบบ (JWT Access Token และข้อมูลผู้ใช้) ลงใน LocalStorage
 * @param {string} accessToken - โทเคน JWT สำหรับใช้ยืนยันสิทธิ์ในคำขอ API
 * @param {object} user - อ็อบเจกต์ข้อมูลโปรไฟล์ของผู้ใช้งาน
 */
function setAuthSession(accessToken, user) {
    localStorage.setItem(AUTH_TOKEN_KEY, accessToken);
    localStorage.setItem(AUTH_USER_KEY, JSON.stringify(user));
}

/**
 * ดึงข้อมูลโปรไฟล์ผู้ใช้งานที่บันทึกไว้ใน LocalStorage
 * @returns {object|null} ข้อมูลผู้ใช้ในรูปแบบ Object หรือ null หากยังไม่ได้ล็อกอิน
 */
function getStoredUser() {
    const raw = localStorage.getItem(AUTH_USER_KEY);
    if (!raw) return null;
    try {
        return JSON.parse(raw);
    } catch {
        return null;
    }
}

/**
 * ล้างข้อมูล Session ทั้งหมดออกจาก LocalStorage (ใช้เมื่อออกจากระบบ / Logout)
 */
function clearAuthSession() {
    localStorage.removeItem(AUTH_TOKEN_KEY);
    localStorage.removeItem(AUTH_USER_KEY);
}

/**
 * นำทางผู้ใช้งานไปยังหน้าเว็บที่สอดคล้องกับบทบาทและสิทธิ์ (Role)
 * - สิทธิ์ผู้ดูแลระบบ (admin) -> นำทางไปหน้า admin.html
 * - สิทธิ์สมาชิกทั่วไป (member) -> นำทางไปหน้า index.html
 * @param {object} user - ข้อมูลผู้ใช้ที่มีฟิลด์ role
 */
function redirectByRole(user) {
    if (user.role === 'admin') {
        window.location.href = 'admin.html';
    } else {
        window.location.href = 'index.html';
    }
}

/**
 * สร้างส่วนหัว HTTP Headers สำหรับคำขอ API โดยจะแนบ Bearer Token ให้อัตโนมัติหากมี Session
 * @param {object} extra - ส่วนหัวเพิ่มเติมที่ต้องการส่งร่วมด้วย
 * @returns {object} อ็อบเจกต์ Headers พร้อมใช้งานสำหรับคำขอ fetch()
 */
function buildAuthHeaders(extra = {}) {
    const token = localStorage.getItem(AUTH_TOKEN_KEY);
    return {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...extra,
    };
}

/**
 * ส่งคำขอ HTTP Request (Fetch API) ไปยัง Backend พร้อมแนบ Headers การยืนยันตัวตนให้อัตโนมัติ
 * @param {string} url - ที่อยู่ API Endpoint
 * @param {object} options - ออปชันเสริม เช่น method, body, headers
 * @returns {Promise<Response>} คำตอบดิบจากเซิร์ฟเวอร์
 */
async function apiFetch(url, options = {}) {
    const headers = buildAuthHeaders(options.headers || {});
    const response = await fetch(url, { ...options, headers });
    return response;
}

// ตัวแปรอ้างอิง authFetch ชี้ไปที่ apiFetch เพื่อรองรับโค้ดในหน้า Dashboard และการยิง API ที่ต้องตรวจสอบสิทธิ์
const authFetch = apiFetch;

/**
 * ส่งคำขอ HTTP Request และแปลงผลลัพธ์ที่ตอบกลับเป็น JSON อัตโนมัติ
 * @param {string} url - ที่อยู่ API Endpoint
 * @param {object} options - ออปชันเสริม
 * @returns {Promise<any>} ข้อมูลผลลัพธ์ในรูปแบบ JSON
 */
async function apiJson(url, options = {}) {
    const response = await apiFetch(url, options);
    return response.json();
}

/**
 * ดึงข้อมูลการตั้งค่าความปลอดภัยและการล็อกอินจาก Backend (เช่น ตรวจสอบว่าเปิดใช้ Google OAuth หรือไม่)
 * @returns {Promise<object>} อ็อบเจกต์สถานะการตั้งค่า { google_login_enabled, google_client_id }
 */
async function fetchAuthConfig() {
    try {
        const result = await apiJson(`${API_BASE}/api/auth/config`);
        if (result.status === 'success') {
            return result.data;
        }
    } catch {
        /* ignore */
    }
    return { google_login_enabled: false, google_client_id: null };
}

/**
 * จัดการ Credential Token ที่ได้รับจาก Google Identity Services
 * ส่งไปตรวจสอบความถูกต้องกับ Backend เพื่อยืนยันตัวตนและบันทึก Session
 * @param {object} response - อ็อบเจกต์คำตอบจาก Google ที่มีฟิลด์ credential
 */
function handleGoogleCredential(response) {
    const credential = response.credential;
    if (!credential) return;

    apiJson(`${API_BASE}/api/auth/google`, {
        method: 'POST',
        body: JSON.stringify({ credential }),
    })
        .then((result) => {
            if (result.status !== 'success') {
                if (typeof showToast === 'function') {
                    showToast(result.message || 'Google login failed');
                } else {
                    alert(result.message || 'Google login failed');
                }
                return;
            }
            setAuthSession(result.access_token, result.user);
            if (result.user.role === 'member') {
                sessionStorage.setItem('tradesensei_just_logged_in', '1');
            }
            redirectByRole(result.user);
        })
        .catch(() => {
            const msg = 'ไม่สามารถเชื่อมต่อเซิร์ฟเวอร์ได้';
            if (typeof showToast === 'function') showToast(msg);
            else alert(msg);
        });
}

/**
 * กำหนดค่าและแสดงผลปุ่ม "ลงชื่อเข้าใช้ด้วย Google" (Google Sign-In Button)
 * หากยังไม่ได้ตั้งค่า Google Client ID จริงใน .env จะแสดงปุ่มแนะนำการตั้งค่าและปุ่มล็อกอิน Demo ให้แทน
 * @param {string} containerId - ID ของ HTML Element ที่จะแสดงปุ่ม
 */
async function initGoogleSignIn(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const config = await fetchAuthConfig();
    if (!config.google_login_enabled || !config.google_client_id) {
        container.innerHTML = `
            <div style="display: flex; flex-direction: column; gap: 8px; width: 100%; max-width: 320px;">
                <button type="button" class="btn-outline" id="google-info-btn" style="display: flex; align-items: center; justify-content: center; gap: 8px; padding: 10px 14px; font-size: 0.9rem;">
                    <svg width="18" height="18" viewBox="0 0 24 24"><path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/><path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"/><path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"/></svg>
                    ลงชื่อเข้าใช้ด้วย Google
                </button>
                <button type="button" class="btn-ghost" id="demo-member-btn" style="font-size: 0.82rem; padding: 6px 12px; color: var(--accent);">
                    ทดลองเข้าสู่ระบบ Demo Member ทันที
                </button>
            </div>
        `;

        document.getElementById('google-info-btn')?.addEventListener('click', () => {
            alert(
                'ข้อมูลการเชื่อมต่อ Google OAuth:\n\n' +
                'ระบบพบว่ายังไม่ได้ระบุ Google OAuth 2.0 Client ID จริงในไฟล์ .env\n' +
                'เพื่อเปิดใช้งาน Google Sign-In จริง:\n' +
                '1. ไปที่ Google Cloud Console (console.cloud.google.com/apis/credentials)\n' +
                '2. สร้าง OAuth 2.0 Client ID (Web Application)\n' +
                '3. ระบุ Authorized JavaScript origins เป็น http://localhost:5500\n' +
                '4. นำ Client ID มาใส่ในไฟล์ .env (GOOGLE_CLIENT_ID=...)\n\n' +
                'หรือคุณสามารถคลิกปุ่ม "ทดลองเข้าสู่ระบบ Demo Member ทันที" ด้านล่างเพื่อใช้งานได้เลยครับ'
            );
        });

        document.getElementById('demo-member-btn')?.addEventListener('click', () => {
            const emailInput = document.getElementById('email');
            const pwdInput = document.getElementById('password');
            if (emailInput && pwdInput) {
                emailInput.value = 'member@example.com';
                pwdInput.value = 'Password123';
                document.getElementById('login-form')?.dispatchEvent(new Event('submit'));
            } else {
                window.location.href = 'login.html';
            }
        });
        return;
    }

    const script = document.createElement('script');
    script.src = 'https://accounts.google.com/gsi/client';
    script.async = true;
    script.defer = true;
    script.onload = () => {
        /* global google */
        if (!window.google?.accounts?.id) return;

        google.accounts.id.initialize({
            client_id: config.google_client_id,
            callback: handleGoogleCredential,
            auto_select: false,
        });

        google.accounts.id.renderButton(container, {
            type: 'standard',
            theme: 'outline',
            size: 'large',
            width: 320,
            text: 'continue_with',
            locale: 'th',
        });
    };
    document.head.appendChild(script);
}

/**
 * จัดการการเปิด-ปิดเมนูนำทาง (Hamburger Menu) สำหรับหน้าจอมือถือและอุปกรณ์ขนาดเล็ก
 * พร้อมเพิ่มการดักจับคลิกพื้นที่ภายนอกเพื่อหุบเมนูเก็บอัตโนมัติ
 */
function initNavToggle() {
    const toggle = document.getElementById('nav-toggle');
    const actions = document.getElementById('nav-actions');
    if (!toggle || !actions) return;

    toggle.addEventListener('click', (e) => {
        e.stopPropagation();
        const isOpen = actions.classList.toggle('nav-open');
        toggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
        toggle.textContent = isOpen ? '✕' : '☰';
    });

    document.addEventListener('click', (e) => {
        if (!actions.classList.contains('nav-open')) return;
        if (actions.contains(e.target) || toggle.contains(e.target)) return;
        actions.classList.remove('nav-open');
        toggle.setAttribute('aria-expanded', 'false');
        toggle.textContent = '☰';
    });

    window.addEventListener('resize', () => {
        if (window.innerWidth > 768) {
            actions.classList.remove('nav-open');
            toggle.setAttribute('aria-expanded', 'false');
            toggle.textContent = '☰';
        }
    });
}

/**
 * ส่งคำขอเปลี่ยนรหัสผ่านของผู้ใช้ไปยัง Backend API
 * @param {string} currentPassword - รหัสผ่านเดิมที่ใช้งานอยู่
 * @param {string} newPassword - รหัสผ่านใหม่ที่ต้องการตั้ง
 * @returns {Promise<object>} ผลลัพธ์การเปลี่ยนรหัสผ่านจากเซิร์ฟเวอร์
 */
async function changeUserPassword(currentPassword, newPassword) {
    return apiJson(`${API_BASE}/api/auth/change-password`, {
        method: 'PUT',
        body: JSON.stringify({
            current_password: currentPassword,
            new_password: newPassword,
        }),
    });
}

/**
 * แสดงกล่องข้อความแจ้งเตือนสั้นๆ (Toast Notification) ที่มุมหน้าจอ
 * @param {string} message - ข้อความที่ต้องการแจ้งให้ผู้ใช้ทราบ
 * @param {number} duration - ระยะเวลาแสดงผล (มิลลิวินาที, ค่าเริ่มต้น 3,500ms)
 */
function showToast(message, duration = 3500) {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container';
        container.setAttribute('aria-live', 'polite');
        document.body.appendChild(container);
    }
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), duration);
}

/**
 * ติดตั้งปุ่มรูปดวงตา (Eye Icon) สำหรับกดดู/ซ่อนรหัสผ่านในทุกช่อง input type="password"
 * มีระบบรักษาตำแหน่งเคอร์เซอร์ และป้องกันไม่ให้คีย์บอร์ดบนมือถือหุบลงขณะกด
 */
function initPasswordVisibility() {
    document.querySelectorAll('input[type="password"]').forEach((input) => {
        if (input.parentElement?.classList.contains('password-field')) return;
        const wrapper = document.createElement('div');
        wrapper.className = 'password-field';
        input.parentNode.insertBefore(wrapper, input);
        wrapper.appendChild(input);

        const toggle = document.createElement('button');
        toggle.type = 'button';
        toggle.className = 'password-toggle';
        toggle.setAttribute('aria-label', 'แสดงรหัสผ่าน');
        toggle.setAttribute('title', 'แสดงหรือซ่อนรหัสผ่าน');
        toggle.tabIndex = -1; // ไม่ขัดจังหวะการกดปุ่ม Tab กรอกฟอร์ม

        const setEyeIcon = (isVisible) => {
            toggle.classList.toggle('is-visible', isVisible);
            toggle.innerHTML = isVisible
                ? '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 3l18 18M10.6 10.6a2 2 0 0 0 2.8 2.8M9.9 4.3A10.8 10.8 0 0 1 12 4c5.2 0 8.7 4.1 9.7 6.1a2 2 0 0 1 0 1.8 12.5 12.5 0 0 1-3.1 3.7M6.2 6.2A12.5 12.5 0 0 0 2.3 10a2 2 0 0 0 0 1.8C3.3 13.9 6.8 18 12 18c.9 0 1.8-.1 2.6-.4"/></svg>'
                : '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M2.3 12a2 2 0 0 1 0-1.8C3.3 8.1 6.8 4 12 4s8.7 4.1 9.7 6.2a2 2 0 0 1 0 1.8C20.7 15.9 17.2 20 12 20S3.3 15.9 2.3 13.8A2 2 0 0 1 2.3 12Z"/><circle cx="12" cy="12" r="3"/></svg>';
        };
        setEyeIcon(false);

        // ป้องกันไม่ให้ input หลุดโฟกัส เพื่อไม่ให้คีย์บอร์ดบนมือถือเด้งหุบเวลาแตะเปิดปิดตา
        const preventBlur = (e) => {
            e.preventDefault();
        };
        toggle.addEventListener('pointerdown', preventBlur);
        toggle.addEventListener('mousedown', preventBlur);

        toggle.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            const wasFocused = document.activeElement === input;
            const showing = input.type === 'text';
            input.type = showing ? 'password' : 'text';
            setEyeIcon(!showing);
            toggle.setAttribute('aria-label', showing ? 'แสดงรหัสผ่าน' : 'ซ่อนรหัสผ่าน');

            // รักษาโฟกัสและตำแหน่งเคอร์เซอร์ให้อยู่ท้ายข้อความเดิม
            if (wasFocused) {
                input.focus();
                const len = input.value.length;
                input.setSelectionRange(len, len);
            }
        });
        wrapper.appendChild(toggle);
    });
}

/**
 * สร้างแถบแสดงความคืบหน้าการเลื่อนหน้าจอ (Scroll Progress Indicator) ที่ด้านบนสุดของหน้าต่าง
 */
function initScrollHelpers() {
    const indicator = document.createElement('div');
    indicator.className = 'scroll-indicator';
    indicator.setAttribute('aria-hidden', 'true');
    document.body.appendChild(indicator);

    let scrollIdleTimer = null;
    const updateScrollUI = () => {
        const maxScroll = document.documentElement.scrollHeight - window.innerHeight;
        const progress = maxScroll > 0 ? window.scrollY / maxScroll : 0;
        indicator.style.transform = `scaleX(${progress})`;
        document.body.classList.toggle('is-scrolled', window.scrollY > 20);
        document.body.classList.add('is-scrolling');
        document.documentElement.style.setProperty('--scroll-progress', progress.toFixed(3));
        window.clearTimeout(scrollIdleTimer);
        scrollIdleTimer = window.setTimeout(() => document.body.classList.remove('is-scrolling'), 160);
    };
    window.addEventListener('scroll', updateScrollUI, { passive: true });
    updateScrollUI();
}

/**
 * จัดการเอฟเฟกต์แอนิเมชันและปฏิสัมพันธ์ของ UI ส่วนกลาง (Micro-interactions)
 * - แสง Spotlight และเอฟเฟกต์เอียง 3D (Tilt) ขณะเลื่อนเมาส์ผ่านการ์ด
 * - การค่อยๆ ปรากฏขึ้นเมื่อเลื่อนหน้าจอมาถึง (Scroll Reveal ด้วย IntersectionObserver)
 * - ระลอกคลื่นน้ำ (Ripple Effect) เมื่อคลิกปุ่มต่างๆ
 */
function initInteractiveSurfaces() {
    const reduceMotion = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
    const surfaces = document.querySelectorAll(
        '.panel, .control-card, .auth-card, .research-step, .news-panel, .analysis-panel'
    );

    surfaces.forEach((surface, index) => {
        surface.classList.add('interactive-surface', 'reveal-on-scroll');
        surface.style.setProperty('--reveal-order', String(Math.min(index, 6)));

        if (reduceMotion) return;
        surface.addEventListener('pointermove', (event) => {
            if (event.pointerType === 'touch') return;
            const rect = surface.getBoundingClientRect();
            const x = (event.clientX - rect.left) / rect.width;
            const y = (event.clientY - rect.top) / rect.height;
            surface.style.setProperty('--spotlight-x', `${Math.max(0, Math.min(100, x * 100))}%`);
            surface.style.setProperty('--spotlight-y', `${Math.max(0, Math.min(100, y * 100))}%`);
            surface.style.setProperty('--tilt-x', `${((0.5 - y) * 2.1).toFixed(2)}deg`);
            surface.style.setProperty('--tilt-y', `${((x - 0.5) * 2.1).toFixed(2)}deg`);
        });
        surface.addEventListener('pointerleave', () => {
            surface.style.removeProperty('--tilt-x');
            surface.style.removeProperty('--tilt-y');
        });
    });

    if ('IntersectionObserver' in window && !reduceMotion) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (!entry.isIntersecting) return;
                entry.target.classList.add('is-visible');
                observer.unobserve(entry.target);
            });
        }, { threshold: 0.12 });
        surfaces.forEach((surface) => observer.observe(surface));
    } else {
        surfaces.forEach((surface) => surface.classList.add('is-visible'));
    }

    document.querySelectorAll('button:not(.password-toggle):not(.modal-close), .btn-primary, .btn-outline, .btn-ai, .btn-ghost').forEach((button) => {
        button.classList.add('interactive-button');
        button.addEventListener('click', (event) => {
            if (button.disabled || reduceMotion) return;
            const rect = button.getBoundingClientRect();
            const ripple = document.createElement('span');
            ripple.className = 'button-ripple';
            ripple.style.left = `${event.clientX - rect.left}px`;
            ripple.style.top = `${event.clientY - rect.top}px`;
            button.appendChild(ripple);
            ripple.addEventListener('animationend', () => ripple.remove(), { once: true });
        });
    });
}

// เริ่มต้นการทำงานของฟังก์ชัน UI เมื่อโหลด DOM เรียบร้อย
document.addEventListener('DOMContentLoaded', () => {
    initNavToggle();
    initPasswordVisibility();
    initScrollHelpers();
    initInteractiveSurfaces();
});
