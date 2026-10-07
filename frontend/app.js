let isLoggedIn = false;
let currentUser = null;
let currentSymbol = 'PTT.BK';
// Members begin with a useful long-term context instead of a single trading day.
let currentChartRange = '1Y';
let isPredictionEnabled = false;
let currentTheme = 'dark';
let chartRequestId = 0;
const stockDataCache = new Map();
const STOCK_CACHE_TTL_MS = 60000;

// แปลงตัวอักษรพิเศษป้องกันโดน XSS
function escapeHtml(value) {
    const element = document.createElement('div');
    element.textContent = String(value ?? '');
    return element.innerHTML;
}

// เช็กว่าเป็นสมาชิกทั่วไป (member) หรือไม่
function isMember() {
    return isLoggedIn && currentUser && currentUser.role === 'member';
}

// เปิด/ปิดช่องพิมพ์แชต Copilot (ถ้าไม่ใช่ member จะกดพิมพ์ไม่ได้)
function setCopilotEditorEnabled(enabled) {
    const editor = document.getElementById('chat-input');
    const button = document.getElementById('chat-send-btn');
    if (editor) {
        editor.contentEditable = enabled ? 'true' : 'false';
        editor.setAttribute('aria-disabled', enabled ? 'false' : 'true');
        editor.tabIndex = enabled ? 0 : -1;
        editor.classList.toggle('is-disabled', !enabled);
    }
    if (button) button.disabled = !enabled;
}

// ปิดเมนู hamburger บนจอมือถือ
function closeNavMenu() {
    const actions = document.getElementById('nav-actions');
    const toggle = document.getElementById('nav-toggle');
    if (actions) actions.classList.remove('nav-open');
    if (toggle) {
        toggle.setAttribute('aria-expanded', 'false');
        toggle.textContent = '☰';
    }
}

// กำหนดธีมสีของหน้าเว็บ (ใช้ดาร์กโหมดเป็นหลัก)
function applyTheme() {
    currentTheme = 'dark';
    document.body.classList.remove('light-theme');
    localStorage.setItem('tradesensei_theme', 'dark');
}

// สลับธีมสี
function toggleTheme() {
    applyTheme();
}

// ล้างสถานะล็อกอินออกจากเครื่อง
function clearLocalAuth() {
    clearAuthSession();
    currentUser = null;
    isLoggedIn = false;
}

// ล็อกปุ่มฟีเจอร์พรีเมียม (เส้นทำนาย, Backtest, Copilot, Timeframe) ถ้ายังไม่ได้ล็อกอิน
function updateLockedControls() {
    const predictionBtn = document.getElementById('prediction-btn');
    const timeMachineBtn = document.getElementById('time-machine-btn');
    const copilotBtn = document.getElementById('copilot-btn');
    const rangeButtons = document.querySelectorAll('.range-btn');

    [predictionBtn, timeMachineBtn, copilotBtn].forEach((btn) => {
        if (!btn) return;
        if (isMember()) {
            btn.classList.remove('locked-btn');
        } else {
            btn.classList.add('locked-btn');
        }
    });

    rangeButtons.forEach((btn) => {
        btn.disabled = !isMember();
    });
}

// ปรับ UI หน้าเว็บตามสถานะล็อกอิน เช่น สลับปุ่มเข้าสู่ระบบ/ออกจากระบบ
function applyAuthUI() {
    const body = document.body;
    const loginBtn = document.getElementById('login-btn');
    const registerBtn = document.getElementById('register-btn');
    const chatInput = document.getElementById('chat-input');
    const chatBtn = document.querySelector('.chat-input-box button');

    const badge = document.getElementById('user-badge');
    const passwordBtn = document.getElementById('password-btn');
    if (isMember()) {
        body.classList.remove('guest-mode');
        body.classList.add('member-mode');
        loginBtn.innerText = 'ออกจากระบบ';
        loginBtn.classList.remove('btn-outline');
        loginBtn.classList.add('btn-ghost');
        registerBtn.style.display = 'none';
        if (passwordBtn) passwordBtn.style.display = 'block';
        setCopilotEditorEnabled(true);
        if (badge && currentUser) {
            badge.textContent = currentUser.first_name || 'สมาชิก';
        }
        if (sessionStorage.getItem('tradesensei_just_logged_in') === '1') {
            sessionStorage.removeItem('tradesensei_just_logged_in');
            document.getElementById('app-dashboard')?.scrollIntoView({ behavior: 'smooth' });
        }
    } else {
        body.classList.remove('member-mode');
        body.classList.add('guest-mode');
        loginBtn.innerText = 'เข้าสู่ระบบ';
        loginBtn.classList.remove('btn-ghost');
        loginBtn.classList.add('btn-outline');
        registerBtn.style.display = 'block';
        if (passwordBtn) passwordBtn.style.display = 'none';
        if (badge) badge.textContent = '';
        setCopilotEditorEnabled(false);
    }

    updateLockedControls();

    if (isMember()) {
        fetchDeepAnalysis(currentSymbol);
    }
}

// กดไปหน้าสมัครสมาชิก
function goToRegister() {
    closeNavMenu();
    window.location.href = 'register.html';
}

// เปิด popup เปลี่ยนรหัสผ่านของสมาชิก
function openPasswordModal() {
    closeNavMenu();
    const modal = document.getElementById('password-modal');
    if (!modal) return;
    document.getElementById('pwd-current').value = '';
    document.getElementById('pwd-new').value = '';
    document.getElementById('pwd-confirm').value = '';
    modal.hidden = false;
}

// ปิด popup เปลี่ยนรหัสผ่าน
function closePasswordModal() {
    const modal = document.getElementById('password-modal');
    if (modal) modal.hidden = true;
}

// ตรวจรหัสผ่านใหม่แล้วส่งไปบันทึกที่เซิร์ฟเวอร์
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

// ปุ่มล็อกอิน/ออกจากระบบบน navbar กดแล้วสลับสถานะ
function handleAuthButton() {
    closeNavMenu();
    if (isLoggedIn) {
        clearLocalAuth();
        isPredictionEnabled = false;
        applyAuthUI();
        drawChart(currentSymbol, isPredictionEnabled);
        window.scrollTo({ top: 0, behavior: 'smooth' });
        return;
    }
    window.location.href = 'login.html';
}

// อ่าน token ตอนโหลดหน้าเว็บ เพื่อดูว่าผู้ใช้ล็อกอินอยู่ไหม
function initAuthFromStorage() {
    const token = localStorage.getItem('tradesensei_token');
    currentUser = getStoredUser();

    if (!token || !currentUser) {
        clearLocalAuth();
        applyAuthUI();
        return;
    }

    if (currentUser.role === 'admin') {
        window.location.href = 'admin.html';
        return;
    }

    if (currentUser.role === 'member') {
        isLoggedIn = true;
        applyAuthUI();
        return;
    }

    clearLocalAuth();
    applyAuthUI();
}

// เลื่อนหน้าจอลงมาที่ส่วนกระดานเทรด (Dashboard)
function scrollToDashboard() {
    document.getElementById('app-dashboard').scrollIntoView({ behavior: 'smooth' });
}

// ดึงข้อมูลผลการทำนายราคาหุ้น 7 วันข้างหน้าจากโมเดล Prophet
async function fetchPrediction(symbol) {
    if (!localStorage.getItem('tradesensei_token')) return null;

    try {
        const response = await apiFetch(`${API_BASE}/api/predict/${symbol}`);
        const result = await response.json();

        if (result.status !== 'success') {
            if (typeof showToast === 'function') showToast(result.message || 'ไม่สามารถสร้างการทำนายได้');
            return null;
        }
        updatePredictionMetrics(result.quality);
        return result;
    } catch (error) {
        console.error('Prediction fetch failed:', error);
        if (typeof showToast === 'function') showToast('ไม่สามารถเชื่อมต่อเซิร์ฟเวอร์สำหรับ AI Prediction ได้');
        return null;
    }
}

// แสดงค่าสถิติความแม่นยำของโมเดล AI (MAE, Accuracy)
function updatePredictionMetrics(quality) {
    const metrics = document.getElementById('prediction-metrics');
    const validation = quality?.validation;
    if (!metrics || !validation?.validation_points || validation.mae == null || validation.accuracy_pct == null) return;
    metrics.hidden = false;
    metrics.replaceChildren();
    [
        `AI Loss (MAE): ${Number(validation.mae).toLocaleString()}`,
        `Accuracy: ${Number(validation.accuracy_pct).toFixed(2)}%`,
        `ทดสอบย้อนหลัง ${validation.validation_points} วัน`,
    ].forEach((label, index) => {
        const badge = document.createElement('span');
        badge.className = `metric-badge metric-${index}`;
        badge.textContent = label;
        metrics.appendChild(badge);
    });
}

// แสดงหรือซ่อนข้อความกำลังโหลดกราฟ
function setChartLoading(visible) {
    const el = document.getElementById('chart-loading');
    if (el) el.classList.toggle('visible', visible);
}

// แปลงช่วงเวลา (1D, 1M, 1Y) เป็นจำนวนแท่งเทียนวันทำการ
function getRangeTradingDays(rangeKey) {
    const map = {
        '1D': 1,
        '7D': 7,
        '1M': 22,
        '6M': 132,
        '1Y': 264,
        '2Y': 528,
    };
    return map[rangeKey] || 132;
}

// ตัดข้อมูลราคาตามช่วงเวลาที่ผู้ใช้กดเลือก
function getFilteredChartData(chartData, rangeKey) {
    const take = Math.min(getRangeTradingDays(rangeKey), chartData.dates.length);
    const start = Math.max(chartData.dates.length - take, 0);
    return {
        dates: chartData.dates.slice(start),
        opens: chartData.opens.slice(start),
        highs: chartData.highs.slice(start),
        lows: chartData.lows.slice(start),
        closes: chartData.closes.slice(start),
    };
}

// คำนวณเส้นค่าเฉลี่ยเคลื่อนที่ SMA (เช่น SMA 20, SMA 50)
function calculateSmaSeries(allCloses, windowSize) {
    if (!allCloses || allCloses.length === 0) return [];

    const rawValues = allCloses.map((_, i) => {
        if (i < windowSize - 1) {
            if (allCloses.length < windowSize && i >= 3) {
                const slice = allCloses.slice(0, i + 1);
                return slice.reduce((sum, n) => sum + n, 0) / slice.length;
            }
            return null;
        }
        const slice = allCloses.slice(i - windowSize + 1, i + 1);
        return slice.reduce((sum, n) => sum + n, 0) / windowSize;
    });

    const filterRadius = windowSize === 20 ? 3 : 5;
    return rawValues.map((val, i) => {
        if (val === null) return null;
        let sum = 0;
        let count = 0;
        for (let k = -filterRadius; k <= filterRadius; k++) {
            const idx = i + k;
            if (idx >= 0 && idx < rawValues.length && rawValues[idx] !== null) {
                const w = filterRadius + 1 - Math.abs(k);
                sum += rawValues[idx] * w;
                count += w;
            }
        }
        return count > 0 ? Number((sum / count).toFixed(2)) : Number(val.toFixed(2));
    });
}

// ไฮไลท์ปุ่มช่วงเวลาที่เลือกอยู่ (1D, 7D, 1M, ฯลฯ)
function updateRangeButtons() {
    document.querySelectorAll('.range-btn').forEach((btn) => {
        btn.classList.toggle('active', btn.dataset.range === currentChartRange);
    });
}

// เปลี่ยนช่วงเวลากราฟ (ฟังก์ชันนี้ใช้ได้เฉพาะสมาชิก)
function setChartRange(rangeKey) {
    if (!isMember()) {
        showToast('ช่วงเวลา 1D/7D/1M/6M/1Y/2Y สำหรับสมาชิกเท่านั้น');
        return;
    }
    currentChartRange = rangeKey;
    updateRangeButtons();
    drawChart(currentSymbol, isPredictionEnabled);
}

// ฟังก์ชันหลักสำหรับวาดกราฟแท่งเทียนด้วย Plotly (รวมเส้นทำนาย AI และ SMA)
async function drawChart(symbol, showAI = false) {
    const requestId = ++chartRequestId;
    let chartData;
    const titleEl = document.getElementById('stock-title');
    const metaEl = document.getElementById('stock-meta');
    if (titleEl) titleEl.innerText = symbol;
    if (metaEl) metaEl.textContent = 'กำลังโหลดกราฟ...';
    setChartLoading(true);

    const cachedEntry = stockDataCache.get(symbol);
    if (cachedEntry && (Date.now() - cachedEntry.timestamp < STOCK_CACHE_TTL_MS)) {
        chartData = cachedEntry.data;
    } else {
        try {
            const response = await apiFetch(`${API_BASE}/api/stock-data/${symbol}`);
            const result = await response.json();
            
            if (result.status === 'success') {
                chartData = result.data;
                stockDataCache.set(symbol, { data: chartData, timestamp: Date.now() });
            } else {
                setChartLoading(false);
                if (metaEl) metaEl.textContent = result.message;
                if (typeof showToast === 'function') showToast(result.message);
                return;
            }
        } catch (error) {
            console.error('Error fetching data:', error);
            setChartLoading(false);
            if (metaEl) metaEl.textContent = 'เชื่อมต่อเซิร์ฟเวอร์ไม่ได้';
            if (typeof showToast === 'function') showToast('ไม่สามารถเชื่อมต่อ Backend ได้');
            return;
        }
    }

    // Ignore an older request that completed after the user selected another stock.
    if (requestId !== chartRequestId) return;

    if (!chartData.dates?.length) {
        if (metaEl) metaEl.textContent = 'ยังไม่มีข้อมูลราคาสำหรับหุ้นนี้';
        if (typeof showToast === 'function') showToast('ยังไม่มีข้อมูลราคาสำหรับหุ้นนี้');
        return;
    }

    setChartLoading(false);
    if (metaEl) {
        const stock = allStocks.find((s) => s.symbol === symbol);
        const visibleData = isMember()
            ? getFilteredChartData(chartData, currentChartRange)
            : chartData;
        metaEl.textContent = stock
            ? `${stock.company_name || ''} · แสดง ${visibleData.dates.length} วัน (${isMember() ? currentChartRange : 'Guest view'})`
            : `แสดง ${visibleData.dates.length} วัน`;
    }

    const visibleData = isMember()
        ? getFilteredChartData(chartData, currentChartRange)
        : chartData;

    // Update MarketChart Header Ticker & Candle Stats
    if (visibleData.closes?.length) {
        const lastClose = visibleData.closes[visibleData.closes.length - 1];
        const prevClose = visibleData.closes.length > 1 ? visibleData.closes[visibleData.closes.length - 2] : lastClose;
        const lastOpen = visibleData.opens?.[visibleData.opens.length - 1] ?? lastClose;
        const lastHigh = visibleData.highs?.[visibleData.highs.length - 1] ?? lastClose;
        const lastLow = visibleData.lows?.[visibleData.lows.length - 1] ?? lastClose;
        const deltaVal = lastClose - prevClose;
        const deltaPct = prevClose > 0 ? (deltaVal / prevClose) * 100 : 0;

        const priceEl = document.getElementById('stock-price');
        const deltaEl = document.getElementById('stock-delta');
        if (priceEl) priceEl.textContent = `฿${lastClose.toFixed(2)}`;
        if (deltaEl) {
            const sign = deltaPct >= 0 ? '+' : '';
            const arrow = deltaPct >= 0 ? '▲' : '▼';
            deltaEl.textContent = `${arrow} ${sign}${deltaPct.toFixed(2)}%`;
            deltaEl.className = `delta-badge ${deltaPct >= 0 ? 'positive' : 'negative'}`;
        }

        const openEl = document.getElementById('stat-open');
        const highEl = document.getElementById('stat-high');
        const lowEl = document.getElementById('stat-low');
        const closeEl = document.getElementById('stat-close');
        const volEl = document.getElementById('stat-vol');
        if (openEl) openEl.textContent = lastOpen.toFixed(2);
        if (highEl) highEl.textContent = lastHigh.toFixed(2);
        if (lowEl) lowEl.textContent = lastLow.toFixed(2);
        if (closeEl) closeEl.textContent = lastClose.toFixed(2);
        if (volEl) volEl.textContent = Math.abs(lastHigh - lastLow).toFixed(2);
    }

    const firstDateStr = visibleData.dates[0];
    const lastDateStr = visibleData.dates[visibleData.dates.length - 1];

    let maxAllowedDateStr = lastDateStr;
    let aiTrace = null;
    let confidenceTrace = null;
    const cssVars = getComputedStyle(document.body);
    const axisColor = cssVars.getPropertyValue('--chart-axis').trim() || '#8B949E';
    const gridColor = cssVars.getPropertyValue('--chart-grid').trim() || '#30363D';
    const upColor = cssVars.getPropertyValue('--chart-up').trim() || '#22C55E';
    const downColor = cssVars.getPropertyValue('--chart-down').trim() || '#F43F5E';
    const predictionColor = cssVars.getPropertyValue('--chart-prediction').trim() || '#00D2FF';
    const confidenceColor = cssVars.getPropertyValue('--chart-confidence').trim() || 'rgba(0, 210, 255, 0.16)';
    const confidenceBorderColor = cssVars.getPropertyValue('--chart-confidence-border').trim()
        || (currentTheme === 'light' ? 'rgba(37, 99, 235, 0.45)' : 'rgba(0, 210, 255, 0.50)');

    // --- 2. เส้นทำนาย AI จาก Facebook Prophet (Backend) ---
    if (showAI && isMember()) {
        const titleEl = document.getElementById('stock-title');
        if (titleEl) titleEl.innerText = `${symbol} (กำลังคำนวณ Prophet...)`;

        try {
            const predictionResult = await fetchPrediction(symbol);
            if (requestId !== chartRequestId) return;

            if (predictionResult && predictionResult.data) {
                const pred = predictionResult.data;

                if (!pred.dates?.length || !pred.closes?.length) {
                    showToast('ยังไม่มีผลการทำนายสำหรับหุ้นนี้');
                } else {
                    const lastPrice = visibleData.closes[visibleData.closes.length - 1];
                    const bridgeDates = [lastDateStr, ...pred.dates];
                    const bridgePrices = [lastPrice, ...pred.closes];
                    maxAllowedDateStr = pred.dates[pred.dates.length - 1];

                    const isMobile = window.innerWidth <= 768;
                    aiTrace = {
                        x: bridgeDates,
                        y: bridgePrices,
                        type: 'scatter',
                        mode: 'lines+markers',
                        line: {
                            color: predictionColor,
                            width: isMobile ? 3.5 : 4,
                            shape: 'spline',
                            smoothing: 0.6,
                            dash: 'dash',
                        },
                        marker: {
                            size: isMobile ? 8 : 9,
                            color: predictionColor,
                            symbol: 'circle',
                            line: {
                                width: 2,
                                color: currentTheme === 'light' ? '#FFFFFF' : '#0B0F19',
                            },
                        },
                        name: predictionResult.cached
                            ? 'AI Forecast (7 วัน, cached)'
                            : 'AI Forecast (ทำนาย 7 วัน)',
                        hovertemplate: '<b>%{x}</b><br>ทำนายราคาปิด: ฿%{y:.2f}<extra>Prophet AI</extra>',
                    };

                    if (pred.lowers && pred.uppers) {
                        confidenceTrace = {
                            x: [...pred.dates, ...pred.dates.slice().reverse()],
                            y: [...pred.uppers, ...pred.lowers.slice().reverse()],
                            type: 'scatter',
                            fill: 'toself',
                            fillcolor: confidenceColor,
                            line: {
                                color: confidenceBorderColor,
                                width: 1.2,
                                dash: 'dot',
                            },
                            name: 'กรอบความเชื่อมั่น 90%',
                            hoverinfo: 'skip',
                        };
                    }
                }
            }
        } catch (predErr) {
            console.warn('Prediction fetch error, proceeding with candlestick chart:', predErr);
        } finally {
            if (titleEl) titleEl.innerText = symbol;
        }
    } else {
        const titleEl = document.getElementById('stock-title');
        if (titleEl && titleEl.innerText.includes('กำลังคำนวณ')) {
            titleEl.innerText = symbol;
        }
    }

    // --- 3. จัดการข้อมูลกราฟแท่งเทียน ---
    const isMobile = window.innerWidth <= 768;
    const historicalTrace = {
        x: visibleData.dates,
        close: visibleData.closes,
        high: visibleData.highs,
        low: visibleData.lows,
        open: visibleData.opens,
        type: 'candlestick',
        name: isMember() ? `ราคา (${currentChartRange})` : 'ราคา (Guest)',
        increasing: { line: { color: upColor, width: isMobile ? 1.6 : 1.4 }, fillcolor: upColor },
        decreasing: { line: { color: downColor, width: isMobile ? 1.6 : 1.4 }, fillcolor: downColor },
        whiskerwidth: 0.6,
        hoverlabel: { bgcolor: 'rgba(17,24,39,0.95)' },
    };

    const volumeColors = visibleData.closes.map((close, i) => (
        close >= visibleData.opens[i] ? 'rgba(34,197,94,0.30)' : 'rgba(244,63,94,0.30)'
    ));
    const volumeTrace = {
        x: visibleData.dates,
        y: visibleData.closes.map((_, i) => Math.abs(visibleData.highs[i] - visibleData.lows[i])),
        type: 'bar',
        yaxis: 'y2',
        marker: { color: volumeColors },
        name: 'Daily Range',
        opacity: isMobile ? 0.28 : 0.45,
        hovertemplate: '%{x}<br>Daily range: %{y:.2f}<extra></extra>',
    };

    const makeSma = (windowSize) => {
        const fullSeries = calculateSmaSeries(chartData.closes, windowSize);
        if (!fullSeries || fullSeries.length === 0) return null;

        const startIdx = Math.max(chartData.dates.length - visibleData.dates.length, 0);
        const visibleValues = fullSeries.slice(startIdx);
        if (!visibleValues.some((v) => v !== null)) return null;

        const isSingleDay = visibleData.dates.length === 1;
        const color = windowSize === 20 ? '#F59E0B' : '#14B8A6';

        if (isSingleDay) {
            const dateStr = visibleData.dates[0];
            const smaVal = visibleValues[0] ?? visibleData.closes[0];
            const candleTime = new Date(dateStr).getTime();
            const tStart = new Date(candleTime - 12 * 3600 * 1000).toISOString();
            const tMid = dateStr;
            const tEnd = new Date(candleTime + 12 * 3600 * 1000).toISOString();

            return {
                x: [tStart, tMid, tEnd],
                y: [smaVal, smaVal, smaVal],
                type: 'scatter',
                mode: 'lines+markers',
                name: `SMA ${windowSize}`,
                line: {
                    width: 2.4,
                    shape: 'linear',
                    color: color,
                },
                marker: {
                    size: 8,
                    color: color,
                },
                hovertemplate: `<b>${dateStr}</b><br>SMA ${windowSize}: ฿%{y:.2f}<extra></extra>`,
            };
        }

        const trace = {
            x: visibleData.dates,
            y: visibleValues,
            type: 'scatter',
            mode: visibleData.dates.length <= 7 ? 'lines+markers' : 'lines',
            name: `SMA ${windowSize}`,
            line: {
                width: 2.2,
                shape: 'linear',
                color: color,
            },
            hovertemplate: `%{x}<br>SMA ${windowSize}: ฿%{y:.2f}<extra></extra>`,
        };
        if (visibleData.dates.length <= 7) {
            trace.marker = {
                size: 6,
                color: color,
            };
        }
        return trace;
    };
    const sma20 = isMember() ? makeSma(20) : null;
    const sma50 = isMember() ? makeSma(50) : null;

    const data = [historicalTrace, volumeTrace];
    if (sma20) data.push(sma20);
    if (sma50) data.push(sma50);
    if (confidenceTrace) data.push(confidenceTrace);
    if (aiTrace) data.push(aiTrace);

    // Keep the chart timeframe scale constant without zooming in
    const isSingleDay = visibleData.dates.length === 1;
    let initialStartDate = firstDateStr;
    let initialEndDate = maxAllowedDateStr;

    if (isSingleDay) {
        const candleTime = new Date(firstDateStr).getTime();
        const spanStart = new Date(candleTime - 14 * 3600 * 1000).toISOString();
        initialStartDate = spanStart;
        if (!showAI || !aiTrace) {
            const spanEnd = new Date(candleTime + 14 * 3600 * 1000).toISOString();
            initialEndDate = spanEnd;
        }
    }

    const layout = {
        title: false,
        dragmode: 'pan',
        margin: isMobile
            ? { r: 16, t: 34, b: 30, l: 38 }
            : { r: 46, t: 12, b: 32, l: 46 },
        showlegend: true,
        xaxis: {
            type: 'date',
            color: axisColor,
            gridcolor: gridColor,
            rangeslider: { visible: false },
            range: [initialStartDate, initialEndDate],
            nticks: isMobile ? 5 : 8,
            tickfont: { size: isMobile ? 9 : 11, color: axisColor },
        },
        yaxis: {
            title: isMobile ? false : { text: 'Price', font: { color: axisColor, size: 11 } },
            color: axisColor,
            gridcolor: gridColor,
            fixedrange: false,
            tickfont: { size: isMobile ? 9 : 11, color: axisColor },
            tickformat: '.2f',
        },
        yaxis2: {
            title: false,
            overlaying: 'y',
            side: 'right',
            showgrid: false,
            showticklabels: false,
            color: axisColor,
        },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        hovermode: 'x unified',
        hoverdistance: 25,
        legend: isMobile
            ? {
                font: { color: axisColor, size: 9 },
                orientation: 'h',
                y: 1.16,
                x: 0,
                bgcolor: 'transparent',
            }
            : {
                font: { color: axisColor },
                orientation: 'h',
                y: 1.12,
                x: 0,
            },
    };

    const config = {
        responsive: true,
        scrollZoom: false,
        displayModeBar: isMobile ? false : 'hover',
        modeBarButtonsToRemove: ['lasso2d', 'select2d', 'autoScale2d'],
    };

    Plotly.newPlot('chart-container', data, layout, config);
}

// ตรวจสอบสถานะสมาชิก ถ้ายังไม่ล็อกอินจะแจ้งเตือนให้เข้าสู่ระบบก่อน
function requireMember(featureName) {
    if (!isMember()) {
        alert(`${featureName} สำหรับสมาชิกเท่านั้น กรุณาเข้าสู่ระบบหรือสมัครสมาชิก`);
        return false;
    }
    return true;
}

// กดปุ่มเปิด/ปิดเส้นทำนาย AI บนกราฟแท่งเทียน
async function togglePrediction() {
    if (!requireMember('เส้นทำนาย AI')) return;

    const btn = document.getElementById('prediction-btn');
    const originalText = btn.textContent;
    btn.disabled = true;
    btn.textContent = 'กำลังคำนวณ Prophet...';

    try {
        isPredictionEnabled = !isPredictionEnabled;
        await drawChart(currentSymbol, isPredictionEnabled);
        if (typeof showToast === 'function') showToast('อัปเดตเส้นทำนาย AI แล้ว');
    } finally {
        btn.disabled = false;
        btn.textContent = originalText;
    }
}

// จัดรูปแบบช่องกรอกเงินลงทุน ใส่คอมม่าคั่นหลักพัน (,) อัตโนมัติ
function initBacktestAmountInput() {
    const input = document.getElementById('backtest-amount');
    if (!input) return;

    const formatInput = () => {
        const rawValue = input.value;
        const cursorPos = input.selectionStart ?? rawValue.length;

        // Count how many numeric digits were before the cursor
        const digitsBeforeCursor = rawValue.slice(0, cursorPos).replace(/\D/g, '').length;

        // Get only digits
        const digits = rawValue.replace(/\D/g, '');
        if (!digits) {
            input.value = '';
            return;
        }

        // Format with thousands comma
        const formatted = Number(digits).toLocaleString('en-US');
        input.value = formatted;

        // Restore cursor position accurately
        let newPos = formatted.length;
        let count = 0;
        for (let i = 0; i < formatted.length; i++) {
            if (/\d/.test(formatted[i])) {
                count++;
            }
            if (count === digitsBeforeCursor) {
                newPos = i + 1;
                break;
            }
        }
        if (digitsBeforeCursor === 0) newPos = 0;
        input.setSelectionRange(newPos, newPos);
    };

    if (!input.dataset.commaBound) {
        input.dataset.commaBound = 'true';
        input.addEventListener('input', formatInput);
    }

    if (input.value && !input.value.includes(',')) {
        const digits = input.value.replace(/\D/g, '');
        if (digits) {
            input.value = Number(digits).toLocaleString('en-US');
        }
    }
}

// เปิด popup เครื่องมือจำลองผลตอบแทน Time Machine
function openBacktestModal() {
    document.getElementById('backtest-modal').hidden = false;
    document.getElementById('backtest-result').innerHTML = '';
    initBacktestAmountInput();
}

// ปิด popup จำลองผลตอบแทน
function closeBacktestModal() {
    document.getElementById('backtest-modal').hidden = true;
}

// กดเปิด Time Machine (ต้องเป็นสมาชิกเท่านั้น)
function toggleTimeMachine() {
    if (!requireMember('Time Machine')) return;
    openBacktestModal();
}

// คำนวณผลตอบแทนย้อนหลัง เทียบระหว่างซื้อหุ้นตัวนี้กับฝากประจำธนาคาร
async function runBacktest() {
    const rawAmount = (document.getElementById('backtest-amount').value || '').replace(/,/g, '').trim();
    const amount = parseFloat(rawAmount);
    const months = parseInt(document.getElementById('backtest-months').value, 10);
    const resultEl = document.getElementById('backtest-result');
    if (!Number.isFinite(amount) || amount < 1000 || !Number.isInteger(months) || months < 1 || months > 24) {
        resultEl.style.display = 'block';
        resultEl.textContent = 'กรุณาระบุเงินลงทุนอย่างน้อย 1,000 บาท และระยะเวลา 1–24 เดือน';
        return;
    }
    resultEl.style.display = 'block';
    resultEl.textContent = 'กำลังจำลองผลตอบแทน...';

    try {
        const response = await authFetch(
            `${API_BASE}/api/backtest/${currentSymbol}`,
            {
                method: 'POST',
                body: JSON.stringify({ initial_amount: amount, months }),
            }
        );
        const result = await response.json();
        if (result.status !== 'success') {
            resultEl.textContent = result.message || 'ไม่สามารถจำลองผลตอบแทนได้';
            return;
        }
        const d = result.data;
        resultEl.replaceChildren();

        const profitLabel = d.stock.profit >= 0 ? 'กำไร' : 'ขาดทุน';
        const formattedProfit = Math.abs(d.stock.profit).toLocaleString('th-TH', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
        const formattedFinalStock = d.stock.final_value.toLocaleString('th-TH', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
        const formattedDepositProfit = Math.abs(d.deposit_benchmark.profit).toLocaleString('th-TH', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
        const formattedDepositFinal = d.deposit_benchmark.final_value.toLocaleString('th-TH', { minimumFractionDigits: 2, maximumFractionDigits: 2 });

        [
            `${d.symbol} (${d.period.start_date} → ${d.period.end_date})`,
            `หุ้น: ${d.stock.return_pct >= 0 ? '+' : ''}${d.stock.return_pct}% (${profitLabel} ${formattedProfit} บาท · รวม ${formattedFinalStock} บาท)`,
            `เงินฝาก ${d.deposit_benchmark.annual_rate_pct}%: ${d.deposit_benchmark.return_pct >= 0 ? '+' : ''}${d.deposit_benchmark.return_pct}% (ดอกเบี้ย +${formattedDepositProfit} บาท · รวม ${formattedDepositFinal} บาท)`,
            d.verdict,
        ].forEach((text, index) => {
            const paragraph = document.createElement('p');
            paragraph.textContent = text;
            if (index === 0 || index === 3) paragraph.style.fontWeight = '700';
            resultEl.appendChild(paragraph);
        });
    } catch (e) {
        resultEl.textContent = 'เชื่อมต่อเซิร์ฟเวอร์ไม่ได้';
    }
}

// ดึงผลวิเคราะห์เจาะลึก (อารมณ์ข่าว TextBlob + แนวโน้มโมเดล Prophet)
async function fetchDeepAnalysis(symbol) {
    if (!isMember()) return;
    const container = document.getElementById('analysis-content');
    if (!container) return;
    container.innerHTML = '<p style="color: var(--text-muted);">กำลังวิเคราะห์ TextBlob + Prophet...</p>';

    try {
        const response = await authFetch(`${API_BASE}/api/analysis/${symbol}`);
        const result = await response.json();
        if (result.status !== 'success') {
            container.textContent = result.message || 'ไม่สามารถโหลดการวิเคราะห์ได้';
            return;
        }
        const a = result.data;
        const s = a.sentiment;
        const tagClass =
            s.overall_label === 'Positive' ? 'sentiment-tag-positive' :
            s.overall_label === 'Negative' ? 'sentiment-tag-negative' : 'sentiment-tag-neutral';

        let html = `
            <p class="analysis-item ${tagClass}">
                <b>อารมณ์ข่าว (${s.average_score >= 0 ? '+' : ''}${s.average_score}):</b>
                ${s.overall_label} (+${s.positive_count} / -${s.negative_count} / =${s.neutral_count})
            </p>
            <p class="analysis-item">
                <b>แนวโน้ม:</b> ${a.trend.direction}
                ${a.trend.forecast_change_pct != null ? ` (พยากรณ์ ${a.trend.forecast_change_pct >= 0 ? '+' : ''}${a.trend.forecast_change_pct}%)` : ''}
            </p>
            <p class="analysis-item" style="color: var(--text-muted); font-size: 0.9rem;">
                ${a.trend.detail}
            </p>
        `;
        if (s.items && s.items.length > 0) {
            html += '<p class="analysis-item"><b>ข่าวล่าสุด:</b></p><ul style="margin:0;padding-left:18px;font-size:0.85rem;">';
            s.items.slice(0, 3).forEach((item) => {
                html += `<li class="${item.label === 'Positive' ? 'sentiment-tag-positive' : item.label === 'Negative' ? 'sentiment-tag-negative' : ''}">${escapeHtml(item.title.substring(0, 60))}...</li>`;
            });
            html += '</ul>';
        }
        const validation = a.forecast_quality?.validation;
        if (validation?.validation_points && validation.mape_pct != null) {
            html += `
                <p class="analysis-item model-quality">
                    <b>คุณภาพโมเดล:</b> Loss (MAE) ${validation.mae ?? '-'} · Accuracy ${validation.accuracy_pct ?? '-'}% · ทดสอบย้อนหลัง ${validation.validation_points} วัน
                </p>`;
        }
        container.innerHTML = html;
    } catch (e) {
        container.innerHTML = '<p style="color:#FF5A5A;">โหลดการวิเคราะห์ไม่สำเร็จ</p>';
    }
}

// ส่งคำถามคุยกับ Sensei Copilot (AI ผู้ช่วยวิเคราะห์หุ้น)
async function sendCopilotMessage() {
    if (!requireMember('Sensei Copilot')) return;
    const input = document.getElementById('chat-input');
    const message = input.textContent.trim();
    if (!message) return;

    const history = document.getElementById('chat-history');
    const userBubble = document.createElement('div');
    userBubble.className = 'message user';
    userBubble.textContent = message;
    history.appendChild(userBubble);
    input.textContent = '';
    setCopilotEditorEnabled(false);

    const loading = document.createElement('div');
    loading.className = 'message ai';
    loading.textContent = 'กำลังคิด...';
    history.appendChild(loading);
    history.scrollTop = history.scrollHeight;

    try {
        const response = await authFetch(`${API_BASE}/api/copilot/chat`, {
            method: 'POST',
            body: JSON.stringify({ symbol: currentSymbol, message }),
        });
        const result = await response.json();
        loading.remove();

        const aiBubble = document.createElement('div');
        aiBubble.className = 'message ai';
        if (result.status === 'success') {
            aiBubble.innerHTML = formatCopilotAiMessage(result.data.response);
        } else {
            aiBubble.textContent = result.message || 'เกิดข้อผิดพลาด';
        }
        history.appendChild(aiBubble);
    } catch (e) {
        loading.remove();
        const err = document.createElement('div');
        err.className = 'message ai';
        err.textContent = 'ไม่สามารถเชื่อมต่อ Copilot ได้';
        history.appendChild(err);
    }

    setCopilotEditorEnabled(true);
    input.focus();
    history.scrollTop = history.scrollHeight;
}

// เปิดหน้าต่างคุยกับ Sensei Copilot
function openCopilotModal() {
    if (!requireMember('Sensei Copilot')) return;
    const modal = document.getElementById('copilot-modal');
    const symbol = document.getElementById('copilot-symbol');
    if (!modal) return;
    if (symbol) symbol.textContent = currentSymbol;
    modal.hidden = false;
    loadCopilotHistory();
    document.getElementById('chat-input')?.focus();
}

// ปิดหน้าต่าง Copilot
function closeCopilotModal() {
    const modal = document.getElementById('copilot-modal');
    if (modal) modal.hidden = true;
}

// ล้างประวัติการคุยกับ Copilot ทั้งหมด
async function clearCopilotHistory() {
    if (!isMember() || !confirm('ลบประวัติการสนทนาทั้งหมดของคุณใช่หรือไม่?')) return;
    const clearButton = document.querySelector('.clear-history-btn');
    if (clearButton) {
        clearButton.disabled = true;
        clearButton.textContent = 'กำลังลบ...';
    }
    try {
        const response = await authFetch(`${API_BASE}/api/copilot/history`, { method: 'DELETE' });
        const result = await response.json();
        if (result.status !== 'success') {
            showToast(result.message || 'ไม่สามารถลบประวัติได้');
            return;
        }
        const history = document.getElementById('chat-history');
        if (history) {
            history.replaceChildren();
            appendChatBubble(history, 'ai', 'เริ่มการสนทนาใหม่ได้เลยครับ ผมพร้อมช่วยวิเคราะห์ข้อมูลของคุณ');
        }
        showToast(result.message || 'ลบประวัติการสนทนาแล้ว');
    } catch {
        showToast('ไม่สามารถเชื่อมต่อเซิร์ฟเวอร์ได้');
    } finally {
        if (clearButton) {
            clearButton.disabled = false;
            clearButton.textContent = 'ลบประวัติ';
        }
    }
}

// จัดรูปแบบข้อความตอบกลับของ AI (แปลง Markdown, ใส่ป้าย Bullish/Bearish)
function formatCopilotAiMessage(rawText) {
    if (!rawText) return '';
    let text = String(rawText);

    // Strip doc citations [D1]-[D9] and any source references
    text = text.replace(/\[D[0-9]\]/g, '');
    text = text.replace(/แหล่งอ้างอิง:.*$/gm, '');

    // Escape HTML to prevent XSS
    const temp = document.createElement('div');
    temp.textContent = text;
    let safeHtml = temp.innerHTML;

    // Convert escaped badge spans back to actual safe badge elements
    safeHtml = safeHtml.replace(
        /&lt;span class=(?:&quot;|"|&#39;|')badge-bullish(?:&quot;|"|&#39;|')&gt;(.*?)&lt;\/span&gt;/gi,
        '<span class="badge-bullish">$1</span>'
    );
    safeHtml = safeHtml.replace(
        /&lt;span class=(?:&quot;|"|&#39;|')badge-bearish(?:&quot;|"|&#39;|')&gt;(.*?)&lt;\/span&gt;/gi,
        '<span class="badge-bearish">$1</span>'
    );
    safeHtml = safeHtml.replace(
        /&lt;span class=(?:&quot;|"|&#39;|')badge-neutral(?:&quot;|"|&#39;|')&gt;(.*?)&lt;\/span&gt;/gi,
        '<span class="badge-neutral">$1</span>'
    );

    // Markdown bold: **text** -> <strong>text</strong>
    safeHtml = safeHtml.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

    // Convert newlines to breaks/paragraphs cleanly
    safeHtml = safeHtml.replace(/\n\n+/g, '<br><br>');
    safeHtml = safeHtml.replace(/\n/g, '<br>');

    return safeHtml;
}

// เพิ่มบอลลูนข้อความใหม่ลงในกล่องแชต
function appendChatBubble(history, type, text, sentAt = '') {
    const bubble = document.createElement('div');
    bubble.className = `message ${type}`;
    if (type === 'ai') {
        bubble.innerHTML = formatCopilotAiMessage(text);
    } else {
        bubble.textContent = text;
    }
    if (sentAt) {
        const time = document.createElement('span');
        time.className = 'message-time';
        time.textContent = sentAt;
        bubble.appendChild(time);
    }
    history.appendChild(bubble);
}

// โหลดประวัติแชตเก่าที่เคยคุยไว้มาแสดง
async function loadCopilotHistory() {
    if (!isMember()) return;
    const history = document.getElementById('chat-history');
    if (!history) return;

    try {
        const response = await authFetch(`${API_BASE}/api/copilot/history`);
        const result = await response.json();
        if (result.status !== 'success' || !result.data?.length) return;

        // Replace only the untouched placeholder greeting. If the member has
        // already sent a new message, avoid inserting older records after it.
        if (!(history.children.length === 1 && history.firstElementChild?.classList.contains('ai'))) return;
        history.replaceChildren();
        result.data.forEach((entry) => {
            appendChatBubble(history, 'user', entry.message, entry.sent_at);
            if (entry.response) appendChatBubble(history, 'ai', entry.response, entry.sent_at);
        });
        history.scrollTop = history.scrollHeight;
    } catch {
        // Keep the friendly empty-state message if the network is unavailable.
    }
}

// เปลี่ยนไปดูหุ้นตัวที่เลือก อัปเดตกราฟ ข่าว และบทวิเคราะห์
function loadStock(symbol, clickedEl) {
    currentSymbol = symbol;
    const copilotSymbol = document.getElementById('copilot-symbol');
    if (copilotSymbol) copilotSymbol.textContent = symbol;
    document.querySelectorAll('#stock-list li').forEach((item) => {
        item.classList.toggle('active', item.dataset.symbol === symbol);
    });
    if (clickedEl && !clickedEl.dataset.symbol) {
        clickedEl.classList.add('active');
    }

    drawChart(symbol, isPredictionEnabled);
    fetchNews(symbol);
    if (isMember()) fetchDeepAnalysis(symbol);
}

let allStocks = [];
let stockSearchQuery = '';

// ฟังก์ชันดึงรายชื่อหุ้นจาก Backend
async function fetchStockList() {
    try {
        const response = await apiFetch(`${API_BASE}/api/stocks`);
        const result = await response.json();
        
        if (result.status === 'success') {
            allStocks = result.data;
            renderStockList('all'); // เรียกฟังก์ชันวาดเมนูซ้าย
        } else {
            document.getElementById('stock-list').textContent = result.message || 'โหลดรายชื่อหุ้นไม่สำเร็จ';
        }
    } catch (error) {
        console.error("Error fetching stocks:", error);
        document.getElementById('stock-list').innerHTML = '<li style="color:red;">โหลดข้อมูลล้มเหลว</li>';
    }
}

// ฟังก์ชันวาดรายชื่อหุ้นลงเมนูด้านซ้าย (รองรับการกรองหมวดหมู่)
function renderStockList(filterCategory) {
    const listContainer = document.getElementById('stock-list');
    listContainer.innerHTML = ''; // ล้างของเก่าทิ้ง

    let filteredStocks = allStocks;
    if (filterCategory !== 'all') {
        filteredStocks = filteredStocks.filter((stock) =>
            stock.category && stock.category.toLowerCase().includes(filterCategory)
        );
    }
    if (stockSearchQuery) {
        const q = stockSearchQuery.toLowerCase();
        filteredStocks = filteredStocks.filter(
            (s) =>
                s.symbol.toLowerCase().includes(q) ||
                (s.company_name && s.company_name.toLowerCase().includes(q))
        );
    }

    // สร้างปุ่มกดรายชื่อหุ้น
    filteredStocks.forEach(stock => {
        const li = document.createElement('li');
        
        // ใส่ไอคอนแยกประเภทให้สวยงาม
        let market = 'US';
        if (stock.symbol.includes('.BK')) market = 'TH';
        else if (stock.category && stock.category.toLowerCase().includes('crypto')) market = 'CR';
        else if (stock.category && (stock.category.toLowerCase().includes('commodit') || stock.category.toLowerCase().includes('gold') || stock.category.toLowerCase().includes('metal'))) market = 'AU';
        else if (['GLD', 'GOLD'].includes(stock.symbol)) market = 'AU';

        // โชว์ตัวย่อหุ้น พร้อมชื่อบริษัทตัวเล็กๆ ด้านล่าง
        li.innerHTML = `
            <div><span class="market-code">${market}</span><strong>${stock.symbol}</strong></div>
            <div style="font-size: 0.8em; color: var(--text-muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                ${escapeHtml(stock.company_name || 'ไม่ระบุชื่อบริษัท')}
            </div>
        `;
        
        // ถ้าเป็นหุ้นที่กำลังดูกราฟอยู่ ให้ไฮไลท์ไว้
        if (stock.symbol === currentSymbol) {
            li.classList.add('active');
        }

        // เมื่อคลิกที่หุ้นตัวนี้ ให้วาดกราฟใหม่
        li.dataset.symbol = stock.symbol;
        li.onclick = () => loadStock(stock.symbol, li);
        listContainer.appendChild(li);
    });

    if(filteredStocks.length === 0) {
        listContainer.innerHTML = '<li style="color:var(--text-muted);">ไม่พบหุ้นในหมวดหมู่นี้</li>';
    }
    const stockCount = document.getElementById('stock-count');
    if (stockCount) stockCount.textContent = `${filteredStocks.length} รายการ`;
}

// ฟังก์ชันดึงข่าวล่าสุดของหุ้น (แก้ใหม่ให้อ่านจาก DB)
async function fetchNews(symbol) {
    const newsList = document.querySelector('.news-panel .news-list');
    newsList.innerHTML = '<li><span style="color: var(--text-muted);">กำลังโหลดข่าวสารจากฐานข้อมูล... ⏳</span></li>';

    try {
        const response = await apiFetch(`${API_BASE}/api/news/${symbol}`);
        const result = await response.json();

        if (result.status === 'success' && result.data.length > 0) {
            newsList.innerHTML = ''; 
            
            result.data.forEach(news => {
                const li = document.createElement('li');
                li.style.marginBottom = "10px"; 
                
                // ดักบั๊ก! ถ้าลิงก์พัง หรือไม่มีลิงก์ ให้โชว์แค่ตัวหนังสือ ไม่ต้องครอบ <a href>
                const safeNewsUrl = getSafeExternalUrl(news.link);
                if (safeNewsUrl) {
                    const link = document.createElement('a');
                    link.href = safeNewsUrl;
                    link.target = '_blank';
                    link.rel = 'noopener noreferrer';
                    link.title = news.title || '';
                    link.textContent = news.title || 'ไม่มีหัวข้อข่าว';
                    li.appendChild(link);
                } else {
                    const title = document.createElement('span');
                    title.textContent = news.title || 'ไม่มีหัวข้อข่าว';
                    li.appendChild(title);
                }
                const published = document.createElement('div');
                published.className = 'news-date';
                published.textContent = news.published_date || 'ล่าสุด';
                li.appendChild(published);
                newsList.appendChild(li);
            });
        } else {
            newsList.innerHTML = '<li><span style="color: var(--text-muted);">ไม่มีข่าวสารสำหรับหุ้นตัวนี้ในฐานข้อมูล</span></li>';
        }
    } catch (error) {
        console.error("Error fetching news:", error);
        newsList.innerHTML = '<li><span style="color: #FF5A5A;">ไม่สามารถเชื่อมต่อฐานข้อมูลข่าวได้</span></li>';
    }
}

// ตรวจสอบความปลอดภัยของ URL ลิงก์ข่าวก่อนเปิด
function getSafeExternalUrl(value) {
    try {
        const url = new URL(String(value || ''), window.location.origin);
        return ['http:', 'https:'].includes(url.protocol) ? url.href : null;
    } catch {
        return null;
    }
}

// ผูก Event ให้กับ Dropdown เลือกหมวดหมู่
document.getElementById('sector-filter')?.addEventListener('change', (e) => {
    renderStockList(e.target.value);
});

document.getElementById('stock-search')?.addEventListener('input', (e) => {
    // A contenteditable search editor prevents browsers from attaching saved
    // login/password suggestions, unlike a regular text input.
    stockSearchQuery = e.target.textContent.trim();
    const sector = document.getElementById('sector-filter')?.value || 'all';
    renderStockList(sector);
});

// Keep dashboard utility fields empty on page load. This also clears values
// restored by browser form-state caching; it never runs after the user types.
window.addEventListener('pageshow', (event) => {
    if (!event.persisted) return;
    const stockSearch = document.getElementById('stock-search');
    const chatInput = document.getElementById('chat-input');
    if (stockSearch) stockSearch.textContent = '';
    if (chatInput) chatInput.textContent = '';
});

document.getElementById('chat-input')?.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendCopilotMessage();
    }
});

document.getElementById('copilot-modal')?.addEventListener('click', (event) => {
    if (event.target.id === 'copilot-modal') closeCopilotModal();
});

document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') closeCopilotModal();
});

// เริ่มต้นลูกเล่นปุ่มและเอฟเฟกต์ไฟบนหน้าแรก (Landing Hero)
function initLandingInteractions() {
    const landing = document.getElementById('landing-page');
    const actions = document.querySelectorAll('[data-landing-action]');
    if (!landing || !actions.length) return;

    const handleLandingAction = (action) => {
        scrollToDashboard();
        window.setTimeout(() => {
            if (action === 'browse') {
                document.getElementById('stock-search')?.focus();
            } else if (action === 'context') {
                document.querySelector('.chart-box')?.scrollIntoView({ behavior: 'smooth', block: 'center' });
            } else if (action === 'analysis') {
                if (isMember()) {
                    document.getElementById('prediction-btn')?.focus();
                    showToast('เลือก Forecast, Backtest หรือ Sensei Copilot เพื่อวิเคราะห์ต่อ');
                } else {
                    showToast('เข้าสู่ระบบเพื่อใช้ Forecast, Backtest และ Sensei Copilot');
                    document.getElementById('login-btn')?.focus();
                }
            }
        }, 520);
    };

    actions.forEach((step) => {
        step.addEventListener('click', () => handleLandingAction(step.dataset.landingAction));
        step.addEventListener('keydown', (event) => {
            if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault();
                handleLandingAction(step.dataset.landingAction);
            }
        });
    });

    // A small pointer light makes the artwork react without moving the content.
    let frameId = null;
    landing.addEventListener('pointermove', (event) => {
        const bounds = landing.getBoundingClientRect();
        const x = ((event.clientX - bounds.left) / bounds.width) * 100;
        const y = ((event.clientY - bounds.top) / bounds.height) * 100;
        if (frameId) cancelAnimationFrame(frameId);
        frameId = requestAnimationFrame(() => {
            landing.style.setProperty('--pointer-x', `${Math.max(0, Math.min(100, x))}%`);
            landing.style.setProperty('--pointer-y', `${Math.max(0, Math.min(100, y))}%`);
        });
    });
}

window.onload = async () => {
    applyTheme(currentTheme);
    initAuthFromStorage();
    updateRangeButtons();
    await fetchStockList();
    drawChart(currentSymbol, isPredictionEnabled);
    fetchNews(currentSymbol);
    if (isMember()) fetchDeepAnalysis(currentSymbol);
    if (isMember()) loadCopilotHistory();
    initLandingInteractions();
    initBacktestAmountInput();
};

