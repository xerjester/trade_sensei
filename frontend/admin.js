// เช็กว่าเป็นแอดมินไหม ถ้าไม่ใช่เตะกลับไปหน้า login หรือหน้าแรก
function requireAdminAuth() {
    const token = localStorage.getItem('tradesensei_token');
    const userRaw = localStorage.getItem('tradesensei_user');
    if (!token || !userRaw) {
        document.body.hidden = true;
        window.location.replace('login.html');
        return false;
    }
    try {
        const user = JSON.parse(userRaw);
        if (user.role !== 'admin') {
            document.body.hidden = true;
            window.location.replace('index.html');
            return false;
        }
        return true;
    } catch {
        localStorage.removeItem('tradesensei_token');
        localStorage.removeItem('tradesensei_user');
        document.body.hidden = true;
        window.location.replace('login.html');
        return false;
    }
}

// แนบ token ใส่ header ไว้ใช้เวลายิง API แอดมิน
function authHeaders() {
    const token = localStorage.getItem('tradesensei_token');
    return {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
    };
}

// แปลงตัวอักษรพิเศษป้องกันโดน XSS บนหน้าแอดมิน
function escapeAdminHtml(value) {
    return String(value ?? '')
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#039;');
}

// ฟังก์ชันจัดรูปแบบข้อความ Log แยกสีตามแท็ก เช่น [Action] สีฟ้า, [Response] สีเขียว, [System] สีม่วง, [Error] สีแดง
function formatLogMessage(rawMessage) {
    const text = String(rawMessage ?? '');
    let escaped = escapeAdminHtml(text);

    // 1. ตรวจจับแท็ก [Tag] ในวงเล็บก้ามปูทั้งหมดในรอบเดียว
    escaped = escaped.replace(/\[([^\]]+)\]/g, (match, tag) => {
        const trimmed = tag.trim();
        const lower = trimmed.toLowerCase();

        // Timestamp เช่น [2026-10-08 17:52:24] หรือ [17:52:24] (สีเทา)
        if (/^\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}$|^\d{2}:\d{2}:\d{2}$/.test(trimmed)) {
            return `<span class="log-tag log-time">[${trimmed}]</span>`;
        }

        // แท็กกลุ่ม Action / การกระทำ / คำสั่งระบบ เช่น [Action], [ADMIN_ADD_STOCK], [FETCH_STOCK_DATA] (สีฟ้าสดใส)
        if (
            lower === 'action' ||
            lower.startsWith('admin') ||
            lower.startsWith('fetch') ||
            lower.startsWith('train') ||
            lower.startsWith('scraper') ||
            lower.includes('stock') ||
            lower.includes('sentiment')
        ) {
            return `<span class="log-tag log-action">[${trimmed}]</span>`;
        }

        // แท็กกลุ่มผลลัพธ์สำเร็จ Response / Success เช่น [Response], [AUTH_LOGIN_SUCCESS] (สีเขียวมิ้นต์)
        if (lower === 'response' || lower.includes('success') || lower.includes('ok')) {
            return `<span class="log-tag log-response">[${trimmed}]</span>`;
        }

        // แท็กกลุ่ม Error / ข้อผิดพลาด เช่น [Error] (สีแดง)
        if (lower === 'error' || lower.includes('fail') || lower.includes('delete')) {
            return `<span class="log-tag log-error">[${trimmed}]</span>`;
        }

        // แท็กกลุ่ม Warning / แจ้งเตือน เช่น [Warning] (สีเหลืองส้ม)
        if (lower === 'warning' || lower.includes('warn')) {
            return `<span class="log-tag log-warning">[${trimmed}]</span>`;
        }

        // แท็กกลุ่ม System / ระบบ เช่น [System], [Info] (สีม่วงลาเวนเดอร์)
        if (lower === 'system' || lower === 'info') {
            return `<span class="log-tag log-system">[${trimmed}]</span>`;
        }

        return `<span class="log-tag log-default">[${trimmed}]</span>`;
    });

    // 2. ปรับสีส่วนชื่อผู้สั่งการ เช่น "by admin@tradesensei.com:"
    escaped = escaped.replace(
        /\bby\s+([^:]+):/g,
        '<span class="log-actor">by $1:</span>'
    );

    return escaped;
}

// เพิ่มบรรทัดข้อความลงกล่อง log ด้านล่าง พร้อมเลื่อนลงล่างสุด และใส่สีสันตามประเภท
function appendLogLine(message) {
    const logWin = document.getElementById('log-window');
    if (!logWin) return;
    const line = document.createElement('div');
    line.className = 'log-line';
    line.innerHTML = formatLogMessage(message);
    logWin.appendChild(line);
    logWin.scrollTop = logWin.scrollHeight;
}

// ตัวแปรและสถานะสำหรับการค้นหาและแบ่งหน้าตารางหุ้น (หน้าละ 10 รายการ)
let allStocks = [];
let filteredStocks = [];
let currentStockPage = 1;
const STOCK_PAGE_SIZE = 10;
let stockSearchQuery = '';

// ฟังก์ชันค้นหาหุ้นแบบเรียลไทม์
function handleStockSearch(query) {
    stockSearchQuery = (query || '').trim().toLowerCase();
    const clearBtn = document.getElementById('clear-stock-search');
    if (clearBtn) clearBtn.style.display = stockSearchQuery ? 'inline-flex' : 'none';
    currentStockPage = 1;
    applyStockFilterAndRender();
}

// ล้างคำค้นหาหุ้น
function clearStockSearch() {
    const input = document.getElementById('stock-search-input');
    if (input) input.value = '';
    handleStockSearch('');
}

// เปลี่ยนหน้าตารางหุ้น (ก่อนหน้า / ถัดไป)
function changeStockPage(delta) {
    const totalPages = Math.max(1, Math.ceil(filteredStocks.length / STOCK_PAGE_SIZE));
    const newPage = currentStockPage + delta;
    if (newPage >= 1 && newPage <= totalPages) {
        currentStockPage = newPage;
        renderStockTablePage();
    }
}

// ไปยังหน้าที่ระบุของตารางหุ้น
function goToStockPage(pageNum) {
    const totalPages = Math.max(1, Math.ceil(filteredStocks.length / STOCK_PAGE_SIZE));
    if (pageNum >= 1 && pageNum <= totalPages) {
        currentStockPage = pageNum;
        renderStockTablePage();
    }
}

// กรองหุ้นตามคำค้นหาแล้วเรนเดอร์ตาราง
function applyStockFilterAndRender() {
    if (!stockSearchQuery) {
        filteredStocks = [...allStocks];
    } else {
        filteredStocks = allStocks.filter((s) => {
            const sym = (s.symbol || '').toLowerCase();
            const name = (s.company_name || '').toLowerCase();
            const cat = (s.category || '').toLowerCase();
            return sym.includes(stockSearchQuery) || name.includes(stockSearchQuery) || cat.includes(stockSearchQuery);
        });
    }
    renderStockTablePage();
}

// เรนเดอร์ตารางหุ้นเฉพาะ 10 รายการในหน้าที่เลือก
function renderStockTablePage() {
    const totalItems = filteredStocks.length;
    const totalPages = Math.max(1, Math.ceil(totalItems / STOCK_PAGE_SIZE));
    if (currentStockPage > totalPages) currentStockPage = totalPages;
    if (currentStockPage < 1) currentStockPage = 1;

    const startIndex = (currentStockPage - 1) * STOCK_PAGE_SIZE;
    const endIndex = Math.min(startIndex + STOCK_PAGE_SIZE, totalItems);
    const pageItems = filteredStocks.slice(startIndex, endIndex);

    const tbody = document.getElementById('stock-table-body');
    if (!tbody) return;
    tbody.innerHTML = '';

    if (pageItems.length === 0) {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td colspan="4" class="table-empty-cell">ไม่พบรายการหุ้นที่ตรงกับคำค้นหา</td>`;
        tbody.appendChild(tr);
    } else {
        pageItems.forEach((stock) => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><b>${escapeAdminHtml(stock.symbol)}</b></td>
                <td>${escapeAdminHtml(stock.company_name || '-')}</td>
                <td>${escapeAdminHtml(stock.category || 'N/A')}</td>
                <td><button type="button" class="btn-delete" data-action="delete-stock">ลบ</button></td>
            `;
            tr.querySelector('[data-action="delete-stock"]')?.addEventListener(
                'click', () => deleteStock(stock.symbol)
            );
            tbody.appendChild(tr);
        });
    }

    // อัปเดตข้อความจำนวนรายการและปุ่มเปลี่ยนหน้า
    const infoEl = document.getElementById('stock-pagination-info');
    if (infoEl) {
        infoEl.textContent = totalItems === 0
            ? 'ไม่พบข้อมูล'
            : `แสดง ${startIndex + 1}-${endIndex} จาก ${totalItems} รายการ`;
    }

    const prevBtn = document.getElementById('stock-prev-btn');
    const nextBtn = document.getElementById('stock-next-btn');
    if (prevBtn) prevBtn.disabled = currentStockPage <= 1;
    if (nextBtn) nextBtn.disabled = currentStockPage >= totalPages;

    // เรนเดอร์ปุ่มหมายเลขหน้า
    const numContainer = document.getElementById('stock-page-numbers');
    if (numContainer) {
        numContainer.innerHTML = '';
        for (let i = 1; i <= totalPages; i++) {
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = `btn-page-number ${i === currentStockPage ? 'active' : ''}`;
            btn.textContent = i;
            btn.onclick = () => goToStockPage(i);
            numContainer.appendChild(btn);
        }
    }
}

// ดึงรายชื่อหุ้นทั้งหมดมาใส่ในตารางจัดการหุ้น
async function loadStocksAdmin() {
    try {
        const response = await fetch(`${API_BASE}/api/stocks`);
        const result = await response.json();
        allStocks = result.data || [];

        // อัปเดตตัวเลขจำนวนหุ้นบนการ์ดสรุป
        const stockCount = document.getElementById('admin-stock-count');
        if (stockCount) stockCount.textContent = allStocks.length;

        applyStockFilterAndRender();
    } catch {
        showToast('โหลดรายชื่อหุ้นไม่ได้');
    }
}

// เพิ่มหุ้นใหม่เข้าสู่ระบบ
async function addStock() {
    const symbol = document.getElementById('new-symbol').value.trim();
    const name = document.getElementById('new-name').value.trim();
    const catInput = document.getElementById('new-category');
    const category = catInput ? catInput.value.trim() : '';

    if (!symbol) {
        showToast('กรุณาระบุชื่อย่อหุ้น');
        return;
    }

    appendLogLine(`[Action] กำลังเพิ่มหุ้น ${symbol.toUpperCase()} และดึงข้อมูลราคา/ข่าว...`);
    const response = await fetch(`${API_BASE}/api/admin/stocks`, {
        method: 'POST',
        headers: authHeaders(),
        body: JSON.stringify({ symbol: symbol, company_name: name, category: category }),
    });
    const result = await response.json();
    showToast(result.message);
    appendLogLine(`[Response] ${result.message}`);
    if (result.status === 'success') {
        document.getElementById('new-symbol').value = '';
        document.getElementById('new-name').value = '';
        if (catInput) catInput.value = '';
        loadStocksAdmin();
        setTimeout(loadLogs, 1500);
    }
}

// ลบหุ้นออกจากระบบ (ถามยืนยันก่อนลบ)
async function deleteStock(symbol) {
    if (!confirm(`ยืนยันการลบหุ้น ${symbol} ออกจากระบบ?`)) return;

    const response = await fetch(`${API_BASE}/api/admin/stocks/${symbol}`, {
        method: 'DELETE',
        headers: authHeaders(),
    });
    const result = await response.json();
    showToast(result.message);
    loadStocksAdmin();
}

// สั่งรันงานเบื้องหลัง เช่น อัปเดตราคาหรือดึงข่าว แล้วพ่นผลลัพธ์ลงกล่อง log
async function runTask(task) {
    appendLogLine(`[Action] เริ่มรันคำสั่ง ${task}...`);

    const response = await fetch(`${API_BASE}/api/admin/${task}`, {
        method: 'POST',
        headers: authHeaders(),
    });
    const result = await response.json();

    appendLogLine(`[Response] ${result.message}`);
    if (typeof showToast === 'function') showToast(result.message);

    if (task === 'train-models' || task === 'run-scraper') {
        setTimeout(loadLogs, 3000);
    }
}

// สั่งเทรนโมเดล AI พยากรณ์ราคาหุ้นใหม่
async function trainModels() {
    await runTask('train-models');
}

// ตัวแปรและสถานะสำหรับการค้นหาและแบ่งหน้าตารางผู้ใช้ (หน้าละ 10 รายการ)
let allUsers = [];
let filteredUsers = [];
let currentUserPage = 1;
const USER_PAGE_SIZE = 10;
let userSearchQuery = '';

// ฟังก์ชันค้นหาผู้ใช้แบบเรียลไทม์
function handleUserSearch(query) {
    userSearchQuery = (query || '').trim().toLowerCase();
    const clearBtn = document.getElementById('clear-user-search');
    if (clearBtn) clearBtn.style.display = userSearchQuery ? 'inline-flex' : 'none';
    currentUserPage = 1;
    applyUserFilterAndRender();
}

// ล้างคำค้นหาผู้ใช้
function clearUserSearch() {
    const input = document.getElementById('user-search-input');
    if (input) input.value = '';
    handleUserSearch('');
}

// เปลี่ยนหน้าตารางผู้ใช้ (ก่อนหน้า / ถัดไป)
function changeUserPage(delta) {
    const totalPages = Math.max(1, Math.ceil(filteredUsers.length / USER_PAGE_SIZE));
    const newPage = currentUserPage + delta;
    if (newPage >= 1 && newPage <= totalPages) {
        currentUserPage = newPage;
        renderUserTablePage();
    }
}

// ไปยังหน้าที่ระบุของตารางผู้ใช้
function goToUserPage(pageNum) {
    const totalPages = Math.max(1, Math.ceil(filteredUsers.length / USER_PAGE_SIZE));
    if (pageNum >= 1 && pageNum <= totalPages) {
        currentUserPage = pageNum;
        renderUserTablePage();
    }
}

// กรองผู้ใช้ตามคำค้นหาแล้วเรนเดอร์ตาราง
function applyUserFilterAndRender() {
    if (!userSearchQuery) {
        filteredUsers = [...allUsers];
    } else {
        filteredUsers = allUsers.filter((u) => {
            const email = (u.email || '').toLowerCase();
            const firstName = (u.first_name || '').toLowerCase();
            const lastName = (u.last_name || '').toLowerCase();
            const fullName = `${firstName} ${lastName}`.trim();
            const role = (u.role || '').toLowerCase();
            const roleLabel = role === 'admin' ? 'admin ผู้ดูแล' : 'member สมาชิก';
            return (
                email.includes(userSearchQuery) ||
                firstName.includes(userSearchQuery) ||
                lastName.includes(userSearchQuery) ||
                fullName.includes(userSearchQuery) ||
                role.includes(userSearchQuery) ||
                roleLabel.includes(userSearchQuery)
            );
        });
    }
    renderUserTablePage();
}

// เรนเดอร์ตารางผู้ใช้เฉพาะ 10 รายการในหน้าที่เลือก
function renderUserTablePage() {
    const totalItems = filteredUsers.length;
    const totalPages = Math.max(1, Math.ceil(totalItems / USER_PAGE_SIZE));
    if (currentUserPage > totalPages) currentUserPage = totalPages;
    if (currentUserPage < 1) currentUserPage = 1;

    const startIndex = (currentUserPage - 1) * USER_PAGE_SIZE;
    const endIndex = Math.min(startIndex + USER_PAGE_SIZE, totalItems);
    const pageItems = filteredUsers.slice(startIndex, endIndex);

    const tbody = document.getElementById('users-table-body');
    if (!tbody) return;
    tbody.innerHTML = '';

    if (pageItems.length === 0) {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td colspan="5" class="table-empty-cell">ไม่พบรายการผู้ใช้ที่ตรงกับคำค้นหา</td>`;
        tbody.appendChild(tr);
    } else {
        const stored = getStoredUser();
        const myId = stored ? stored.user_id : null;

        pageItems.forEach((user) => {
            const name = [user.first_name, user.last_name].filter(Boolean).join(' ') || '-';
            const roleLabel = user.role === 'admin' ? 'Admin' : 'Member';
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${escapeAdminHtml(user.email)}</td>
                <td>${escapeAdminHtml(name)}</td>
                <td><span class="role-badge role-${escapeAdminHtml(user.role)}">${roleLabel}</span></td>
                <td>${escapeAdminHtml(user.created_at || '-')}</td>
                <td class="table-actions">
                    <button type="button" class="btn-edit" data-action="edit-user">แก้ไข</button>
                    ${user.user_id !== myId ? '<button type="button" class="btn-delete" data-action="delete-user">ลบ</button>' : '<span class="text-muted">(คุณ)</span>'}
                </td>
            `;
            tr.querySelector('[data-action="edit-user"]')?.addEventListener(
                'click', () => openUserEdit(user.user_id)
            );
            tr.querySelector('[data-action="delete-user"]')?.addEventListener(
                'click', () => deleteUser(user.user_id, user.email)
            );
            tbody.appendChild(tr);
        });
    }

    // อัปเดตข้อความจำนวนรายการและปุ่มเปลี่ยนหน้า
    const infoEl = document.getElementById('user-pagination-info');
    if (infoEl) {
        infoEl.textContent = totalItems === 0
            ? 'ไม่พบข้อมูล'
            : `แสดง ${startIndex + 1}-${endIndex} จาก ${totalItems} บัญชี`;
    }

    const prevBtn = document.getElementById('user-prev-btn');
    const nextBtn = document.getElementById('user-next-btn');
    if (prevBtn) prevBtn.disabled = currentUserPage <= 1;
    if (nextBtn) nextBtn.disabled = currentUserPage >= totalPages;

    // เรนเดอร์ปุ่มหมายเลขหน้า
    const numContainer = document.getElementById('user-page-numbers');
    if (numContainer) {
        numContainer.innerHTML = '';
        for (let i = 1; i <= totalPages; i++) {
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = `btn-page-number ${i === currentUserPage ? 'active' : ''}`;
            btn.textContent = i;
            btn.onclick = () => goToUserPage(i);
            numContainer.appendChild(btn);
        }
    }
}

// โหลดรายชื่อผู้ใช้ทั้งหมดมาแสดงในตารางจัดการสมาชิก
async function loadUsers() {
    try {
        const response = await fetch(`${API_BASE}/api/admin/users`, { headers: authHeaders() });
        const result = await response.json();
        if (result.status !== 'success') {
            showToast(result.message || 'โหลดรายชื่อผู้ใช้ไม่ได้');
            return;
        }

        allUsers = result.data || [];
        usersCache = allUsers;

        // อัปเดตตัวเลขจำนวนผู้ใช้บนการ์ดสรุป
        const userCount = document.getElementById('admin-user-count');
        if (userCount) userCount.textContent = allUsers.length;

        applyUserFilterAndRender();
    } catch {
        showToast('โหลดรายชื่อผู้ใช้ไม่ได้');
    }
}

let usersCache = [];

// เปิดหน้าต่างแก้ไขข้อมูลผู้ใช้
async function openUserEdit(userId) {
    try {
        const response = await fetch(`${API_BASE}/api/admin/users`, { headers: authHeaders() });
        const result = await response.json();
        if (result.status !== 'success') {
            showToast(result.message || 'โหลดข้อมูลไม่ได้');
            return;
        }
        usersCache = result.data;
        const user = usersCache.find((u) => u.user_id === userId);
        if (!user) return;

        document.getElementById('edit-user-id').value = user.user_id;
        document.getElementById('edit-email').value = user.email;
        document.getElementById('edit-first-name').value = user.first_name || '';
        document.getElementById('edit-last-name').value = user.last_name || '';
        document.getElementById('edit-role').value = user.role;
        document.getElementById('edit-new-password').value = '';
        document.getElementById('user-edit-modal').hidden = false;
    } catch {
        showToast('โหลดข้อมูลไม่ได้');
    }
}

// ปิดหน้าต่างแก้ไขข้อมูลผู้ใช้
function closeUserEditModal() {
    document.getElementById('user-edit-modal').hidden = true;
}

// บันทึกข้อมูลผู้ใช้ที่แก้ไข ส่งไปอัปเดตที่เซิร์ฟเวอร์
async function saveUserEdit() {
    const userId = document.getElementById('edit-user-id').value;
    const payload = {
        email: document.getElementById('edit-email').value.trim(),
        first_name: document.getElementById('edit-first-name').value.trim(),
        last_name: document.getElementById('edit-last-name').value.trim(),
        role: document.getElementById('edit-role').value,
    };
    const newPassword = document.getElementById('edit-new-password').value;
    if (newPassword) payload.new_password = newPassword;

    const response = await fetch(`${API_BASE}/api/admin/users/${userId}`, {
        method: 'PUT',
        headers: authHeaders(),
        body: JSON.stringify(payload),
    });
    const result = await response.json();
    if (result.status === 'success') {
        showToast(result.message);
        closeUserEditModal();
        loadUsers();
    } else {
        showToast(result.message || 'บันทึกไม่สำเร็จ');
    }
}

// ลบผู้ใช้ออกจากระบบ (ถามยืนยันก่อนลบ)
async function deleteUser(userId, email) {
    if (!confirm(`ยืนยันการลบผู้ใช้ ${email}?`)) return;

    const response = await fetch(`${API_BASE}/api/admin/users/${userId}`, {
        method: 'DELETE',
        headers: authHeaders(),
    });
    const result = await response.json();
    showToast(result.message || (result.status === 'success' ? 'ลบสำเร็จ' : 'ลบไม่สำเร็จ'));
    if (result.status === 'success') loadUsers();
}

// เปิดหน้าต่างเปลี่ยนรหัสผ่านแอดมิน
function openPasswordModal() {
    document.getElementById('pwd-current').value = '';
    document.getElementById('pwd-new').value = '';
    document.getElementById('pwd-confirm').value = '';
    document.getElementById('password-modal').hidden = false;
}

// ปิดหน้าต่างเปลี่ยนรหัสผ่านแอดมิน
function closePasswordModal() {
    document.getElementById('password-modal').hidden = true;
}

// ตรวจความถูกต้องของรหัสผ่านใหม่ แล้วส่งเปลี่ยนรหัสผ่าน
async function submitPasswordChange() {
    const current = document.getElementById('pwd-current').value;
    const newPwd = document.getElementById('pwd-new').value;
    const confirm = document.getElementById('pwd-confirm').value;

    if (!current || !newPwd) {
        showToast('กรุณากรอกรหัสผ่านปัจจุบันและรหัสผ่านใหม่');
        return;
    }
    if (newPwd.length < 8 || !/[A-Za-z]/.test(newPwd) || !/\d/.test(newPwd)) {
        showToast('รหัสผ่านใหม่ต้องมีอย่างน้อย 8 ตัว และมีตัวอักษรกับตัวเลข');
        return;
    }
    if (newPwd !== confirm) {
        showToast('รหัสผ่านใหม่ไม่ตรงกัน');
        return;
    }

    try {
        const result = await changeUserPassword(current, newPwd);
        if (result.status === 'success') {
            showToast(result.message || 'เปลี่ยนรหัสผ่านสำเร็จ');
            closePasswordModal();
        } else {
            showToast(result.message || 'เปลี่ยนรหัสผ่านไม่สำเร็จ');
        }
    } catch {
        showToast('ไม่สามารถเชื่อมต่อเซิร์ฟเวอร์ได้');
    }
}

// ดึง log การทำงานของระบบ 25 รายการล่าสุดมาโชว์ในกล่อง log
async function loadLogs() {
    const logWin = document.getElementById('log-window');
    try {
        const response = await fetch(`${API_BASE}/api/admin/logs?limit=25`, { headers: authHeaders() });
        const result = await response.json();
        if (result.status !== 'success') {
            appendLogLine(`[Error] ${result.message}`);
            return;
        }
        logWin.replaceChildren();
        appendLogLine('[System] Logs ล่าสุด');
        result.data.forEach((log) => {
            const actor = log.user_email ? `${log.user_email}${log.user_role ? ` (${log.user_role})` : ''}` : 'system';
            appendLogLine(`[${log.created_at}] [${log.action_type}] by ${actor}: ${log.description}`);
        });
        logWin.scrollTop = logWin.scrollHeight;
    } catch (e) {
        appendLogLine('[Error] โหลด Log ไม่ได้');
    }
}

// ออกจากระบบ ลบข้อมูล token ทิ้ง แล้วกลับไปหน้า login
function logoutAdmin() {
    localStorage.removeItem('tradesensei_token');
    localStorage.removeItem('tradesensei_user');
    window.location.href = 'login.html';
}

// ล้างค่าที่เบราว์เซอร์แอบ autofill อัตโนมัติในช่องฟอร์มหุ้น
function clearStockFormAutofill() {
    ['new-symbol', 'new-name', 'new-category'].forEach((id) => {
        const el = document.getElementById(id);
        if (el && (el.value === 'admin' || el.value.includes('@') || el.value.toLowerCase() === 'admin')) {
            el.value = '';
        }
    });
}

// ตอนเปิดหน้าเว็บ เช็กสิทธิ์แอดมินก่อน ถ้าผ่านค่อยโหลดข้อมูลหุ้น ผู้ใช้ และ log มาแสดง
window.onload = () => {
    if (!requireAdminAuth()) return;   // ไม่ใช่แอดมิน หยุดทำงานทันที
    document.body.hidden = false;      // ผ่านแล้ว ค่อยเปิดให้เห็นหน้าเว็บ
    clearStockFormAutofill();
    setTimeout(clearStockFormAutofill, 50);
    setTimeout(clearStockFormAutofill, 200);
    setTimeout(clearStockFormAutofill, 500);
    loadStocksAdmin();
    loadUsers();
    loadLogs();
};
