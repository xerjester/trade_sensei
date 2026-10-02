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

function authHeaders() {
    const token = localStorage.getItem('tradesensei_token');
    return {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
    };
}

function escapeAdminHtml(value) {
    return String(value ?? '')
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#039;');
}

function appendLogLine(message) {
    const logWin = document.getElementById('log-window');
    const line = document.createElement('div');
    line.textContent = String(message ?? '');
    logWin.appendChild(line);
    logWin.scrollTop = logWin.scrollHeight;
}

async function loadStocksAdmin() {
    const response = await fetch(`${API_BASE}/api/stocks`);
    const result = await response.json();
    const tbody = document.getElementById('stock-table-body');
    tbody.innerHTML = '';

    result.data.forEach(stock => {
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

    // Keep the operations overview in sync with the master-data table.
    const stockCount = document.getElementById('admin-stock-count');
    if (stockCount) stockCount.textContent = result.data.length;
}

async function addStock() {
    const symbol = document.getElementById('new-symbol').value.trim();
    const name = document.getElementById('new-name').value.trim();

    if (!symbol) {
        showToast('กรุณาระบุชื่อย่อหุ้น');
        return;
    }

    const response = await fetch(`${API_BASE}/api/admin/stocks`, {
        method: 'POST',
        headers: authHeaders(),
        body: JSON.stringify({ symbol: symbol, company_name: name }),
    });
    const result = await response.json();
    showToast(result.message);
    if (result.status === 'success') {
        document.getElementById('new-symbol').value = '';
        document.getElementById('new-name').value = '';
        loadStocksAdmin();
    }
}

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

async function trainModels() {
    await runTask('train-models');
}

async function loadUsers() {
    const tbody = document.getElementById('users-table-body');
    if (!tbody) return;

    try {
        const response = await fetch(`${API_BASE}/api/admin/users`, { headers: authHeaders() });
        const result = await response.json();
        if (result.status !== 'success') {
            showToast(result.message || 'โหลดรายชื่อผู้ใช้ไม่ได้');
            return;
        }

        const stored = getStoredUser();
        const myId = stored ? stored.user_id : null;
        tbody.innerHTML = '';

        result.data.forEach((user) => {
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

        // The header is a quick readout, while the table remains the source of detail.
        const userCount = document.getElementById('admin-user-count');
        if (userCount) userCount.textContent = result.data.length;
    } catch {
        showToast('โหลดรายชื่อผู้ใช้ไม่ได้');
    }
}

let usersCache = [];

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

function closeUserEditModal() {
    document.getElementById('user-edit-modal').hidden = true;
}

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

function openPasswordModal() {
    document.getElementById('pwd-current').value = '';
    document.getElementById('pwd-new').value = '';
    document.getElementById('pwd-confirm').value = '';
    document.getElementById('password-modal').hidden = false;
}

function closePasswordModal() {
    document.getElementById('password-modal').hidden = true;
}

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
            appendLogLine(`[${log.created_at}] ${log.action_type} by ${actor}: ${log.description}`);
        });
        logWin.scrollTop = logWin.scrollHeight;
    } catch (e) {
        appendLogLine('[Error] โหลด Log ไม่ได้');
    }
}

function logoutAdmin() {
    localStorage.removeItem('tradesensei_token');
    localStorage.removeItem('tradesensei_user');
    window.location.href = 'login.html';
}

window.onload = () => {
    if (!requireAdminAuth()) return;   // redirect fired — stop all JS
    document.body.hidden = false;      // show page only when auth confirmed
    loadStocksAdmin();
    loadUsers();
    loadLogs();
};
