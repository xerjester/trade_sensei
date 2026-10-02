# TradeSensei — Test Case Specification

**Test framework:** pytest + Flask test client  
**Automated suite:** `backend/tests/`  
**Test environment:** isolated SQLite database, no live Yahoo Finance, Gemini,
Resend, scheduler, or Prophet execution.

## วิธีรันทดสอบ

```powershell
docker compose exec backend pytest
```

ผลล่าสุด: **120 passed, 0 failed, 0 errors, 0 skipped** (7 August 2026)

ชุดทดสอบแยกกรณีย่อยเป็นรหัส `A/B/C` เช่น TC-06A รายการหุ้น,
TC-06B ราคา OHLCV และ TC-06C ข่าว เพื่อให้ผลบน Terminal ระบุได้ชัดเจนว่า
ส่วนใดผ่านหรือไม่ผ่าน

## ขอบเขต Automated Test ปัจจุบัน

| กลุ่ม | จำนวนที่ pytest รัน | สิ่งที่ตรวจสอบ |
|---|---:|---|
| `TC-*` Core acceptance | 22 | Guest, authentication, member ownership และ admin master data |
| `API-*` Feature workflows | 17 | Business API ทุก route, OTP, Forecast, Analysis, Backtest, Copilot และ background tasks |
| `SEC-*` Security | 29 | SQL injection, XSS, JWT, IDOR, CORS, CSP, payload limit, enumeration, secrets, hashing, rate limit, command injection และ mass assignment |
| `UI-*` Buttons/controls | 52 | ปุ่มและ form ทุกหน้า, endpoint/handler ที่ถูกเรียก, modal/navigation, accessibility และ output encoding |
| **รวม** | **120** | **ผ่านทั้งหมดในการรันล่าสุด** |

ไฟล์ทดสอบแยกตามกลุ่ม:

- `backend/tests/test_public_and_auth_api.py` — Core Guest/Auth
- `backend/tests/test_member_and_admin_api.py` — Member/Admin ownership
- `backend/tests/test_feature_workflows.py` — Feature success paths
- `backend/tests/test_security_api.py` — OWASP/adversarial tests
- `backend/tests/test_ui_controls.py` — ปุ่มและ UI contracts
- `backend/tests/test_route_inventory.py` — บังคับให้ route ใหม่ต้องถูกเพิ่มใน test inventory

หมายเหตุ: ชุด `UI-*` ตรวจ wiring และผลลัพธ์ที่กำหนดใน HTML/JavaScript ทุกปุ่ม
โดยอัตโนมัติ แต่การคลิกบน browser engine จริงและ dialog ของระบบควรรันซ้ำใน
staging เมื่อมี Chrome/Playwright runner พร้อมใช้งาน

---

## 1. API และความปลอดภัย

### TC-01 — ตรวจสอบสถานะ API และ Security Headers

| รายการ | รายละเอียด |
|---|---|
| วัตถุประสงค์ | ยืนยันว่า API เริ่มใช้งานได้และส่ง HTTP security headers พื้นฐาน |
| ความเกี่ยวข้อง | ระบบส่วนกลาง / OWASP hardening |
| เงื่อนไขก่อนทดสอบ | Backend ทำงานอยู่ |
| ขั้นตอนทดสอบ | 1. ส่ง `GET /`<br>2. ตรวจ HTTP status, JSON และ response headers |
| ข้อมูลทดสอบ | ไม่มี |
| ผลที่คาดหวัง | ได้ `200`, `status: success`, `X-Content-Type-Options: nosniff` และ `X-Frame-Options: DENY` |
| สถานะ | Automated — `test_health_check_exposes_safe_response_and_security_headers` |

### TC-02 — ปฏิเสธข้อมูลเขียน API ที่ไม่ใช่ JSON

| รายการ | รายละเอียด |
|---|---|
| วัตถุประสงค์ | ป้องกัน request ที่มี content type ไม่ชัดเจนก่อนถึง business logic |
| ความเกี่ยวข้อง | OWASP input validation |
| เงื่อนไขก่อนทดสอบ | Backend ทำงานอยู่ |
| ขั้นตอนทดสอบ | ส่ง `POST /api/auth/login` พร้อม body แบบ plain text โดยไม่กำหนด `application/json` |
| ข้อมูลทดสอบ | `email=a@example.com` |
| ผลที่คาดหวัง | ได้ `415` และ JSON `status: error` |
| สถานะ | Automated — `test_api_write_rejects_non_json_payload` |

### TC-03 — สมัครสมาชิก เข้าสู่ระบบ และอ่านข้อมูลตนเอง

| รายการ | รายละเอียด |
|---|---|
| วัตถุประสงค์ | ตรวจสอบ workflow 1.1 สมัครสมาชิก และ 1.2 เข้าสู่ระบบ |
| ความเกี่ยวข้อง | D1 `users`, JWT authentication |
| เงื่อนไขก่อนทดสอบ | อีเมลยังไม่เคยลงทะเบียน |
| ขั้นตอนทดสอบ | 1. `POST /api/auth/register`<br>2. `POST /api/auth/login` ด้วยข้อมูลชุดเดียวกัน<br>3. นำ access token ไปเรียก `GET /api/auth/me` |
| ข้อมูลทดสอบ | `ADA@Example.com`, รหัสผ่าน `SecurePass1` |
| ผลที่คาดหวัง | สมัครสำเร็จ `201`, อีเมลถูก normalize เป็นตัวพิมพ์เล็ก, login ได้ JWT และ `/me` คืนข้อมูลสมาชิกถูกต้อง |
| สถานะ | Automated — `test_register_login_and_current_user_flow` |

### TC-04 — ป้องกันรหัสผ่านอ่อนและอีเมลซ้ำ

| รายการ | รายละเอียด |
|---|---|
| วัตถุประสงค์ | บังคับ password policy และ unique email |
| ความเกี่ยวข้อง | D1 `users`, Authentication security |
| เงื่อนไขก่อนทดสอบ | ไม่มี |
| ขั้นตอนทดสอบ | 1. สมัครด้วยรหัส `password`<br>2. สมัครด้วยอีเมลที่ถูกต้อง<br>3. สมัครซ้ำด้วยอีเมลเดิม |
| ข้อมูลทดสอบ | `weak@example.com`, `valid@example.com`, `SecurePass1` |
| ผลที่คาดหวัง | รหัสผ่านอ่อนได้ `400`; การสมัครครั้งแรกได้ `201`; อีเมลซ้ำได้ `400` และไม่มีบัญชีเพิ่ม |
| สถานะ | Automated — `test_registration_rejects_weak_or_duplicate_credentials` |

### TC-05 — ปฏิเสธการเข้าถึงของ Member ที่ไม่มี JWT

| รายการ | รายละเอียด |
|---|---|
| วัตถุประสงค์ | ยืนยันว่า endpoint ของสมาชิกไม่เปิดเผยข้อมูลส่วนตัวต่อ Guest |
| ความเกี่ยวข้อง | JWT authorization, D6 `chat_history` |
| เงื่อนไขก่อนทดสอบ | ไม่มี token |
| ขั้นตอนทดสอบ | เรียก `GET /api/auth/me` และ `GET /api/copilot/history` โดยไม่ส่ง Authorization header |
| ข้อมูลทดสอบ | ไม่มี |
| ผลที่คาดหวัง | ทุก request ได้ `401` และ JSON `status: error` |
| สถานะ | Automated — `test_member_endpoints_require_a_valid_jwt` |

---

## 2. ฟังก์ชันผู้ใช้งานทั่วไป (Guest)

### TC-06 — แสดงรายการหุ้น ราคา และข่าว

| รายการ | รายละเอียด |
|---|---|
| วัตถุประสงค์ | ตรวจสอบข้อมูลที่ Dashboard ใช้แสดงผล |
| ความเกี่ยวข้อง | D2 `stocks`, D3 `historical_prices`, D4 `news`; DFD 4.1 |
| เงื่อนไขก่อนทดสอบ | มีหุ้น `PTT.BK`, ราคา 1 วัน และข่าว 1 รายการในฐานข้อมูล |
| ขั้นตอนทดสอบ | 1. `GET /api/stocks`<br>2. `GET /api/stock-data/ptt.bk`<br>3. `GET /api/news/PTT.BK` |
| ข้อมูลทดสอบ | ราคา close `30.50`, หัวข้อข่าว `PTT update` |
| ผลที่คาดหวัง | ได้ชื่อหุ้น, OHLCV ที่เรียงตามวันที่ และข่าวพร้อมลิงก์ |
| สถานะ | Automated — `test_public_stock_price_and_news_data_flow` |

### TC-07 — ป้องกัน Symbol ที่รูปแบบไม่ถูกต้อง

| รายการ | รายละเอียด |
|---|---|
| วัตถุประสงค์ | ยืนยัน allow-list ของ stock symbol และลดความเสี่ยง injection/path manipulation |
| ความเกี่ยวข้อง | Input validation, D2–D4 |
| เงื่อนไขก่อนทดสอบ | ไม่มี |
| ขั้นตอนทดสอบ | เรียก `GET /api/stock-data/bad%20symbol` และ `GET /api/news/<script>` |
| ข้อมูลทดสอบ | Symbol ที่มี space และ HTML tag |
| ผลที่คาดหวัง | ได้ `400`; ไม่มีการ query หรือเรียกข้อมูลภายนอก |
| สถานะ | Automated — `test_public_routes_reject_invalid_stock_symbols` |

---

## 3. ฟังก์ชันสมาชิก (Member)

### TC-08 — สมาชิกเห็นเฉพาะประวัติ Copilot ของตนเอง

| รายการ | รายละเอียด |
|---|---|
| วัตถุประสงค์ | ป้องกันการรั่วไหลของประวัติการสนทนาระหว่างผู้ใช้ |
| ความเกี่ยวข้อง | D6 `chat_history`, DFD 5.1 |
| เงื่อนไขก่อนทดสอบ | สมาชิก A และ B มีข้อความสนทนาคนละ 1 รายการ |
| ขั้นตอนทดสอบ | ใช้ JWT ของสมาชิก A เรียก `GET /api/copilot/history` |
| ข้อมูลทดสอบ | `first question` ของ A, `second question` ของ B |
| ผลที่คาดหวัง | Response มีเฉพาะ `first question` และไม่มีข้อความของ B |
| สถานะ | Automated — `test_copilot_history_is_limited_to_current_member_and_can_be_cleared` |

### TC-09 — สมาชิกสามารถลบเฉพาะประวัติ Copilot ของตนเอง

| รายการ | รายละเอียด |
|---|---|
| วัตถุประสงค์ | ยืนยันการลบ D6 แบบแยกตามเจ้าของข้อมูล |
| ความเกี่ยวข้อง | D6 `chat_history`, D7 `system_logs`; DFD 5.5 |
| เงื่อนไขก่อนทดสอบ | สมาชิก A และ B มีข้อความสนทนาคนละ 1 รายการ |
| ขั้นตอนทดสอบ | ใช้ JWT ของ A ส่ง `DELETE /api/copilot/history` แล้วตรวจข้อมูลทั้ง A และ B |
| ข้อมูลทดสอบ | Chat history ของสมาชิก 2 คน |
| ผลที่คาดหวัง | ลบของ A ได้ 1 รายการ, ของ B ยังอยู่ และระบบบันทึก audit log |
| สถานะ | Automated — `test_copilot_history_is_limited_to_current_member_and_can_be_cleared` |

### TC-10 — ตรวจสอบข้อมูล Backtest และ Copilot ก่อนประมวลผล

| รายการ | รายละเอียด |
|---|---|
| วัตถุประสงค์ | ไม่ให้ service คำนวณหรือ RAG ทำงานกับ input ที่ผิด |
| ความเกี่ยวข้อง | DFD 4.3, 5.2; input validation |
| เงื่อนไขก่อนทดสอบ | มี JWT ของ member |
| ขั้นตอนทดสอบ | 1. `POST /api/backtest/AAPL` ด้วย `months: invalid`<br>2. `POST /api/copilot/chat` ด้วย symbol ไม่ถูกต้อง<br>3. ส่ง message ยาว 1,001 ตัวอักษร |
| ข้อมูลทดสอบ | `bad symbol!`, message `x` 1,001 ตัว |
| ผลที่คาดหวัง | ทุกกรณีได้ `400` และไม่เรียก Backtest/Copilot service |
| สถานะ | Automated — `test_member_validation_blocks_bad_backtest_and_copilot_input` |

---

## 4. ฟังก์ชันผู้ดูแลระบบ (Administrator)

### TC-11 — Member ไม่สามารถเข้าหน้า API สำหรับ Admin

| รายการ | รายละเอียด |
|---|---|
| วัตถุประสงค์ | บังคับ role separation |
| ความเกี่ยวข้อง | DFD 6.1–6.2, admin authorization |
| เงื่อนไขก่อนทดสอบ | มี JWT ของ role `member` |
| ขั้นตอนทดสอบ | เรียก `GET /api/admin/logs` ด้วย JWT ของ member |
| ข้อมูลทดสอบ | JWT role `member` |
| ผลที่คาดหวัง | ได้ `403` และไม่มี D7 log ถูกเปิดเผย |
| สถานะ | Automated — `test_member_cannot_use_admin_routes` |

### TC-12 — Admin เพิ่มหุ้นและป้องกันหุ้นซ้ำ

| รายการ | รายละเอียด |
|---|---|
| วัตถุประสงค์ | ตรวจ Master Data Management |
| ความเกี่ยวข้อง | D2 `stocks`, DFD 2.1 |
| เงื่อนไขก่อนทดสอบ | มี JWT ของ role `admin` |
| ขั้นตอนทดสอบ | 1. `POST /api/admin/stocks` ด้วย symbol `aapl`<br>2. ส่งคำขออีกครั้งด้วย `AAPL` |
| ข้อมูลทดสอบ | `Apple Inc.`, category `Technology` |
| ผลที่คาดหวัง | คำขอแรกได้ `201` และ normalize เป็น `AAPL`; คำขอซ้ำได้ `400` |
| สถานะ | Automated — `test_admin_can_add_normalized_stock_and_read_filtered_logs` |

### TC-13 — Admin ค้นหา System Log ด้วยตัวกรอง

| รายการ | รายละเอียด |
|---|---|
| วัตถุประสงค์ | ยืนยันการอ่าน D7 log และ query filter |
| ความเกี่ยวข้อง | D7 `system_logs`, DFD 6.1–6.2 |
| เงื่อนไขก่อนทดสอบ | มี admin และ log action `TEST_A`, `TEST_B` |
| ขั้นตอนทดสอบ | เรียก `GET /api/admin/logs?action_type=TEST_A&limit=1` |
| ข้อมูลทดสอบ | `TEST_A`, `TEST_B` |
| ผลที่คาดหวัง | ได้ `200`, จำนวนไม่เกิน 1 และได้เฉพาะ `TEST_A` |
| สถานะ | Automated — `test_admin_can_add_normalized_stock_and_read_filtered_logs` |

---

## 5. กรณีทดสอบแบบ Manual / Controlled Environment

> กรณีต่อไปนี้ไม่ควรรันกับ production data หรือ credentials จริง เพราะเรียก
> external API หรือใช้การประมวลผลโมเดลที่ใช้เวลานาน

### TC-14 — Data Scraper บันทึกราคาและข่าว

| รายการ | รายละเอียด |
|---|---|
| วัตถุประสงค์ | ทดสอบ pipeline Admin → Yahoo Finance → D3/D4 |
| เงื่อนไขก่อนทดสอบ | Yahoo fixture หรือ sandbox ที่กำหนดผลลัพธ์ได้; admin account |
| ขั้นตอนทดสอบ | กด **ดึงข้อมูลตลาด** หรือ `POST /api/admin/run-scraper`; รอ task จบ; ตรวจ D3, D4 และ D7 |
| ผลที่คาดหวัง | OHLCV ถูก clean และไม่ซ้ำตาม `(stock_id, date)`; ข่าวมีลิงก์; D7 มีผลสำเร็จ/ผิดพลาด |
| สถานะ | Manual / integration |

### TC-15 — Prophet สร้างผลทำนาย 7 วันและ quality metadata

| รายการ | รายละเอียด |
|---|---|
| วัตถุประสงค์ | ทดสอบ Data pipeline ขั้น Train/Forecast |
| เงื่อนไขก่อนทดสอบ | หุ้น fixture มีราคาย้อนหลังเพียงพอสำหรับการเทรน |
| ขั้นตอนทดสอบ | สั่ง **เทรน Prophet ทั้งหมด**; ตรวจ `price_predictions` และ `stock_models` |
| ผลที่คาดหวัง | D5 มี forecast 7 วันทำการ พร้อม close/lower/upper และ quality metadata เช่น MAE/MAPE |
| สถานะ | Manual / integration |

### TC-16 — วิเคราะห์ Sentiment ของข่าว

| รายการ | รายละเอียด |
|---|---|
| วัตถุประสงค์ | ตรวจ TextBlob sentiment pipeline |
| เงื่อนไขก่อนทดสอบ | เตรียมข่าวภาษาอังกฤษ positive, neutral, negative ที่ทราบผล |
| ขั้นตอนทดสอบ | รัน sentiment service แล้วตรวจ `news_sentiments` |
| ผลที่คาดหวัง | ทุกข่าวมี score, label (`Positive`/`Neutral`/`Negative`) และเวลา `analyzed_at` |
| สถานะ | Manual / service integration |

### TC-17 — Deep Analysis ดึงข้อมูลจาก D3–D5

| รายการ | รายละเอียด |
|---|---|
| วัตถุประสงค์ | ตรวจข้อมูลเชิงลึกของสมาชิก |
| เงื่อนไขก่อนทดสอบ | มีข้อมูลราคา ข่าว sentiment และผลทำนายของหุ้นเดียวกัน |
| ขั้นตอนทดสอบ | ใช้ JWT member เรียก `GET /api/analysis/<symbol>` |
| ผลที่คาดหวัง | ได้ trend component และ sentiment breakdown ที่สอดคล้องกับข้อมูลที่จัดเตรียม |
| สถานะ | Manual / integration |

### TC-18 — Copilot ใช้เฉพาะข้อมูลในระบบ

| รายการ | รายละเอียด |
|---|---|
| วัตถุประสงค์ | ตรวจ strict grounding ของ RAG และ fallback เมื่อไม่มี Gemini key |
| เงื่อนไขก่อนทดสอบ | เตรียม D3–D5 ที่มีตัวเลข/ข่าวเฉพาะเจาะจง และสร้าง 2 environment: มี/ไม่มี `GEMINI_API_KEY` |
| ขั้นตอนทดสอบ | ใช้ JWT member ส่งคำถามเดียวกันไปที่ `POST /api/copilot/chat` ทั้งสอง environment |
| ผลที่คาดหวัง | คำตอบอ้างอิงเฉพาะ facts ที่เตรียมไว้, ไม่สร้างคำแนะนำซื้อขายหรือข้อมูลภายนอก; ไม่มี key ต้องได้ deterministic fallback |
| สถานะ | Manual / AI integration |

### TC-19 — OTP รีเซ็ตรหัสผ่าน

| รายการ | รายละเอียด |
|---|---|
| วัตถุประสงค์ | ตรวจ Forgot Password ด้วย Resend และ single-use OTP |
| เงื่อนไขก่อนทดสอบ | Resend sandbox inbox และ member ที่ตั้งรหัสผ่านด้วยระบบปกติ |
| ขั้นตอนทดสอบ | 1. `POST /api/auth/forgot-password`<br>2. อ่าน OTP จาก sandbox inbox<br>3. `POST /api/auth/reset-password`<br>4. login ด้วยรหัสใหม่<br>5. ลองใช้ OTP เดิมซ้ำ |
| ผลที่คาดหวัง | OTP มีอายุ 10 นาที, เปลี่ยนรหัสได้ครั้งเดียว, login ใหม่สำเร็จ, OTP เดิมถูกปฏิเสธ |
| สถานะ | Manual / email integration |

### TC-20 — Async Admin Tasks และ Log

| รายการ | รายละเอียด |
|---|---|
| วัตถุประสงค์ | ตรวจการสั่ง scraper/train แบบ background และการติดตามผล |
| เงื่อนไขก่อนทดสอบ | Admin account, scheduler และ scripts พร้อมทำงาน |
| ขั้นตอนทดสอบ | ส่ง `POST /api/admin/run-scraper` และ `POST /api/admin/train-models`; ตรวจ status ทันทีและติดตาม Log |
| ผลที่คาดหวัง | API ตอบ `202` โดยไม่รอ process จบ; ระบบเพิ่ม D7 log ที่บอกผลหรือ error ของ task |
| สถานะ | Manual / integration |

### TC-21 — Browser UX และ Responsive Layout

| รายการ | รายละเอียด |
|---|---|
| วัตถุประสงค์ | ตรวจการใช้งานจริงของ Guest, Member และ Admin |
| เงื่อนไขก่อนทดสอบ | เปิด frontend และ backend; browser desktop และ mobile viewport |
| ขั้นตอนทดสอบ | ตรวจ navbar, login, stock search, chart, Copilot modal, Admin Log และ user table ที่ความกว้าง 1440px, 768px, 375px |
| ผลที่คาดหวัง | ไม่มีองค์ประกอบล้นจอ; modal ปิด/เปิดได้; controls กดได้; ใช้ keyboard focus ได้ |
| สถานะ | Manual / UI acceptance |

---

## Traceability summary

| DFD data store | Test cases |
|---|---|
| D1 `users` | TC-03, TC-04, TC-05, TC-11, TC-19 |
| D2 `stocks` | TC-06, TC-07, TC-12, TC-14 |
| D3 `historical_prices` | TC-06, TC-14, TC-15, TC-17, TC-18 |
| D4 `news` / `news_sentiments` | TC-06, TC-14, TC-16, TC-17, TC-18 |
| D5 `price_predictions` / `stock_models` | TC-15, TC-17, TC-18 |
| D6 `chat_history` | TC-08, TC-09, TC-18 |
| D7 `system_logs` | TC-09, TC-13, TC-14, TC-20 |
