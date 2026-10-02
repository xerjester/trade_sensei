# บทที่ 4 — ผลการทดสอบระบบ TradeSensei

**วันที่ทดสอบ:** 7 สิงหาคม พ.ศ. 2569  
**วิธีการทดสอบ:** Black Box Testing  
**เครื่องมือ:** pytest 8.4.2 · Flask Test Client · Docker Compose (Python 3.10.20)  
**ผลรวม: 120 passed · 0 failed · 0 errors · 0 skipped**

---

## 4.1 วิธีการทดสอบระบบ

ผู้จัดทำทดสอบระบบด้วยเทคนิค **Black Box Testing** โดยพิจารณาข้อมูลนำเข้าและผลลัพธ์ที่ระบบแสดงออกมาเท่านั้น โดยไม่คำนึงถึงโครงสร้างภายในของซอร์สโค้ด สภาพแวดล้อมในการทดสอบใช้ฐานข้อมูล SQLite แบบแยกเฉพาะ ไม่กระทบฐานข้อมูลจริง และบริการภายนอกอย่าง Yahoo Finance, Gemini, Resend และ Prophet ถูกจำลอง (Mock) ให้ผลคงที่

**ตารางที่ 4.1 สรุปผลการทดสอบอัตโนมัติแยกตามกลุ่ม**

| กลุ่มการทดสอบ | จำนวนกรณีทดสอบ | ผ่าน | ไม่ผ่าน |
|---|---:|---:|---:|
| ฟังก์ชันหลักของระบบ (Core Acceptance) | 22 | 22 | 0 |
| การทำงานของ API และ Workflow | 17 | 17 | 0 |
| ความปลอดภัยของระบบ (Security) | 29 | 29 | 0 |
| ปุ่ม ฟอร์ม และส่วนควบคุมหน้าเว็บ (UI Controls) | 52 | 52 | 0 |
| **รวมทั้งสิ้น** | **120** | **120** | **0** |

$$\text{อัตราการผ่าน} = \frac{120}{120} \times 100 = \textbf{ร้อยละ 100}$$

---

## 4.2 ผลการทดสอบหน้าลงทะเบียน (Register)

| รหัส | กรณีทดสอบ | ข้อมูลนำเข้า | ผลที่คาดหวัง | ผลที่ได้รับ | ผล |
|---|---|---|---|---|:---:|
| TC-03A | สมัครสมาชิกด้วยข้อมูลถูกต้อง | ชื่อ `Ada`, อีเมล `ADA@Example.com`, รหัสผ่าน `SecurePass1` | Status `201`, อีเมลถูก normalize เป็น `ada@example.com`, role = `member` | Status `201`, อีเมล = `ada@example.com`, role = `member` | ✅ |
| TC-04A | สมัครด้วยรหัสผ่านไม่ผ่านเกณฑ์ | รหัสผ่าน `password` (ตัวพิมพ์เล็กล้วน) | Status `400`, `status: error` | Status `400`, `status: error` | ✅ |
| TC-04B | สมัครด้วยอีเมลที่มีในระบบแล้ว | อีเมล `valid@example.com` ที่ลงทะเบียนซ้ำ | Status `400`, `status: error` | Status `400`, `status: error` | ✅ |
| SEC-05 | สมัครด้วยชื่อที่มี HTML Tag | `first_name: <img src=x onerror=alert(1)>` | Status `400` ปฏิเสธก่อนบันทึก | Status `400`, `status: error` | ✅ |
| SEC-07 | สมัครด้วยอีเมลที่มีอักขระ SQL | `email: victim@example.com' OR '1'='1` | Status `400` ปฏิเสธ | Status `400`, `status: error` | ✅ |
| SEC-20 | สมัครพร้อมส่ง field `role: admin` (Mass Assignment) | payload เพิ่ม `"role": "admin"` และ `"is_admin": true` | Status `201`, role ถูก force เป็น `member` | Status `201`, role = `member` | ✅ |
| UI-25 | ปุ่มเมนู (Hamburger) เปิด/ปิด Navigation | คลิก `#nav-toggle` | Navigation toggle และมี attribute `nav-open` | Handler และ token ถูกผูกครบ | ✅ |
| UI-26 | ปุ่มสมัครสมาชิกส่งฟอร์มและบันทึก Session | submit `#register-form` | เรียก `/api/auth/register`, บันทึก Session, redirect ไป `index.html` | Endpoint และ handler ผูกครบ | ✅ |

---

## 4.3 ผลการทดสอบหน้าเข้าสู่ระบบ (Login)

| รหัส | กรณีทดสอบ | ข้อมูลนำเข้า | ผลที่คาดหวัง | ผลที่ได้รับ | ผล |
|---|---|---|---|---|:---:|
| TC-03B | เข้าสู่ระบบด้วยข้อมูลถูกต้อง | อีเมล `ada@example.com`, รหัสผ่าน `SecurePass1` | Status `200`, ได้ JWT Access Token | Status `200`, มี `access_token` | ✅ |
| TC-03B | นำ JWT ไปอ่านข้อมูลตนเอง | Bearer Token จากขั้นตอนก่อน | Status `200`, ได้ข้อมูลสมาชิกถูกต้อง | Status `200`, `email: ada@example.com` | ✅ |
| TC-02 | ส่ง Request แบบ Plain Text (ไม่ใช่ JSON) | `POST /api/auth/login` ด้วย `Content-Type` ไม่ถูกต้อง | Status `415`, `status: error` | Status `415`, `status: error` | ✅ |
| SEC-01 | Login ด้วย SQL Injection | `email: ' OR 1=1 --`, `password: ' OR 1=1 --` | Status `401` ไม่ได้ Token | Status `401`, ไม่มี `access_token` | ✅ |
| SEC-04 | ส่ง JWT ปลอมหรือเสียรูปแบบ | `Authorization: Bearer not-a-valid-jwt` | Status `401`, `status: error` | Status `401`, `status: error` | ✅ |
| SEC-10 | Login ด้วยรหัสผ่านผิด (อีเมลมีในระบบ vs ไม่มี) | รหัสผ่าน `WrongPass1` กับอีเมล known และ unknown | ข้อความ Error เหมือนกันทั้งสองกรณี (ป้องกัน Enumeration) | Status `401` และข้อความเหมือนกันทุก field | ✅ |
| SEC-18 | Login เกิน 5 ครั้งภายใน 1 นาที (Brute-Force) | ส่ง request ผิดซ้ำ 6 ครั้ง | ครั้งที่ 1–5 ได้ `401`, ครั้งที่ 6 ได้ `429` | Status ตรงตามที่คาดทุกครั้ง | ✅ |
| SEC-06 | ส่ง Payload ขนาดเกิน 1 MB | `password: 'x' × 1,048,577 ตัวอักษร` | Status `413`, `status: error` | Status `413`, `status: error` | ✅ |
| UI-19 | ปุ่มเมนูหน้า Login เปิด/ปิด Navigation | คลิก `#nav-toggle` | Navigation toggle | Handler ผูกครบ | ✅ |
| UI-20 | ปุ่ม Login ส่งฟอร์มและบันทึก Session | submit `#login-form` | เรียก `/api/auth/login`, บันทึก Session, redirect ตาม Role | Endpoint, `setAuthSession`, `redirectByRole` ผูกครบ | ✅ |
| UI-21 | ปุ่ม "ลืมรหัสผ่าน" เปิด OTP Modal | คลิก `#forgot-password-btn` | Modal `forgot-password-modal` ปรากฏ | Handler เปิด Modal ได้ | ✅ |
| UI-22 | ปุ่มปิด Forgot Password ซ่อน Modal | คลิก `#forgot-password-close` | Modal ซ่อน | `closeForgotPasswordModal` ถูกเรียก | ✅ |
| UI-23 | ปุ่มส่ง OTP ขอรีเซ็ตรหัสผ่าน | submit `#request-otp-form` | เรียก `/api/auth/forgot-password` | Endpoint ผูกครบ | ✅ |
| UI-24 | ปุ่มตั้งรหัสใหม่ด้วย OTP | submit `#reset-password-form` | เรียก `/api/auth/reset-password` | Endpoint ผูกครบ | ✅ |

---

## 4.4 ผลการทดสอบหน้าหลัก — Dashboard (index.html)

### 4.4.1 ฟังก์ชัน Guest (ไม่ต้องเข้าสู่ระบบ)

| รหัส | กรณีทดสอบ | ข้อมูลนำเข้า | ผลที่คาดหวัง | ผลที่ได้รับ | ผล |
|---|---|---|---|---|:---:|
| TC-01 | ตรวจสอบ API ทำงานและส่ง Security Headers | `GET /` | Status `200`, `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY` | ครบทุก Header | ✅ |
| TC-06A | แสดงรายการหุ้นบน Dashboard | `GET /api/stocks` (มี `PTT.BK` ในฐานข้อมูล) | Status `200`, ได้ Symbol `PTT.BK` | Status `200`, Symbol ถูกต้อง | ✅ |
| TC-06B | แสดงกราฟราคา OHLCV | `GET /api/stock-data/ptt.bk` | Status `200`, `closes: [30.5]` | Status `200`, ราคาถูกต้อง | ✅ |
| TC-06C | แสดงรายการข่าวหุ้น | `GET /api/news/PTT.BK` | Status `200`, ได้ข่าวพร้อม title และ URL | Status `200`, title = `PTT update` | ✅ |
| TC-07A | ค้นหาหุ้นด้วย Symbol ผิดรูปแบบ (มีช่องว่าง) | `GET /api/stock-data/bad%20symbol` | Status `400` ก่อนเข้าถึงฐานข้อมูล | Status `400`, `status: error` | ✅ |
| TC-07B | ค้นหาหุ้นด้วย Symbol ที่มี HTML Tag | `GET /api/news/<script>` | Status `400` | Status `400`, `status: error` | ✅ |
| SEC-02 | ค้นหาหุ้นด้วย SQL Injection ใน Symbol | `GET /api/stock-data/AAPL' OR 1=1--` | Status `400` ก่อน Query | Status `400`, `status: error` | ✅ |
| SEC-12 | เรียก API จาก Origin ที่ไม่ได้รับอนุญาต | `GET /api/stocks` พร้อม `Origin: https://evil.example` | ไม่มี `Access-Control-Allow-Origin` header | Header ไม่ปรากฏ | ✅ |
| SEC-13 | ตรวจ Content Security Policy | `GET /` | Header มี `default-src 'self'`, `object-src 'none'`, `frame-ancestors 'none'` | ครบทุก directive | ✅ |
| SEC-14 | เรียก Endpoint ที่ไม่มีอยู่ | `GET /api/does-not-exist` | Status `404`, ไม่มี Stack Trace หรือ SQLAlchemy ใน response | Status `404`, JSON ปลอดภัย | ✅ |
| UI-01 | ปุ่มเมนู (Hamburger) เปิด/ปิด Navigation | คลิก `#nav-toggle` | Navigation toggle, `aria-expanded` เปลี่ยน | Handler ผูกครบ | ✅ |
| UI-02 | ปุ่ม "เข้าสู่ระบบ" ไปหน้า Login | คลิก `#login-btn` | redirect ไป `login.html` | `handleAuthButton()` ผูกครบ | ✅ |
| UI-03 | ปุ่ม "สมัครฟรี" ไปหน้า Register | คลิก `#register-btn` | redirect ไป `register.html` | `goToRegister()` ผูกครบ | ✅ |
| UI-04 | ปุ่ม "สำรวจตลาด" เลื่อนไป Dashboard | คลิก `button[onclick="scrollToDashboard()"]` | เลื่อน scroll ไปยัง `#app-dashboard` | Handler ผูกครบ | ✅ |
| UI-09 | ปุ่มสมัครใน Locked Analysis Section | คลิกปุ่มใน `.locked-overlay` | redirect ไป `register.html` | Handler ผูกครบ | ✅ |
| UI-44 | ลิงก์ข่าวอนุญาตเฉพาะ HTTP/HTTPS | URL ข่าว | บล็อก `javascript:` URL | มี `getSafeExternalUrl` ตรวจ protocol | ✅ |

### 4.4.2 ฟังก์ชัน Member (ต้องเข้าสู่ระบบ)

| รหัส | กรณีทดสอบ | ข้อมูลนำเข้า | ผลที่คาดหวัง | ผลที่ได้รับ | ผล |
|---|---|---|---|---|:---:|
| TC-05A | เรียก `/api/auth/me` โดยไม่มี JWT | ไม่ส่ง Authorization header | Status `401`, `status: error` | Status `401` | ✅ |
| TC-05B | เรียก `/api/copilot/history` โดยไม่มี JWT | ไม่ส่ง Authorization header | Status `401`, `status: error` | Status `401` | ✅ |
| API-06 | ดูผลทำนายราคา 7 วัน (Forecast) | `GET /api/predict/AAPL` พร้อม JWT | Status `200`, ได้ dates 7 วัน, MAE = 1.20 | dates 7 วัน, MAE = 1.20 | ✅ |
| API-07 | ดูผลวิเคราะห์เชิงลึก (Deep Analysis) | `GET /api/analysis/aapl` พร้อม JWT | Status `200`, ได้ trend และ sentiment | Status `200`, ได้ข้อมูลครบ | ✅ |
| API-08 | จำลองผลตอบแทน (Backtest) | `POST /api/backtest/AAPL`, เงิน 100,000 บาท, 1 เดือน | Status `200`, `return_pct: 10.0`, มี `deposit_benchmark` | Status `200`, ผลตอบแทนถูกต้อง | ✅ |
| TC-10A | ส่ง Backtest ด้วยค่า months ไม่ถูกต้อง | `months: "invalid"` | Status `400` ก่อนคำนวณ | Status `400`, `status: error` | ✅ |
| API-03 | เปลี่ยนรหัสผ่านและ Login ด้วยรหัสใหม่ | `PUT /api/auth/change-password`, รหัสเดิม `SecurePass1`, รหัสใหม่ `NewSecure2` | Status `200`, login ด้วยรหัสเก่าไม่ได้, รหัสใหม่ได้ | Status `200`, Login ถูกต้อง | ✅ |
| UI-05 | ปุ่ม Forecast เปิด/ปิดผลทำนาย | คลิก `#prediction-btn` | เรียก `/api/predict/`, toggle `isPredictionEnabled` | Handler และ Endpoint ผูกครบ | ✅ |
| UI-06 | ปุ่ม Backtest เปิด Time Machine Modal | คลิก `#time-machine-btn` | Modal `backtest-modal` ปรากฏ | `toggleTimeMachine()` ผูกครบ | ✅ |
| UI-07 | ปุ่ม Ask Sensei เปิด Copilot Modal | คลิก `#copilot-btn` | Modal `copilot-modal` ปรากฏ | `openCopilotModal()` ผูกครบ | ✅ |
| UI-08A–F | ปุ่มช่วงกราฟ 1D / 7D / 1M / 6M / 1Y / 2Y | คลิกปุ่มแต่ละช่วงเวลา | เปลี่ยน `currentChartRange` ตรงตามที่กด | Handler ผูกครบทั้ง 6 ปุ่ม | ✅ |

### 4.4.3 ฟังก์ชัน Copilot Modal (Sensei Copilot)

| รหัส | กรณีทดสอบ | ข้อมูลนำเข้า | ผลที่คาดหวัง | ผลที่ได้รับ | ผล |
|---|---|---|---|---|:---:|
| TC-08 | ดูประวัติสนทนาเห็นเฉพาะของตนเอง | `GET /api/copilot/history` ด้วย JWT ของสมาชิก A | ได้เฉพาะ `first question` ของ A ไม่มีของ B | ได้ 1 รายการ ถูกต้อง | ✅ |
| TC-09 | ลบประวัติสนทนาลบเฉพาะของตนเอง | `DELETE /api/copilot/history` ด้วย JWT ของ A | ลบของ A ได้ 1 รายการ ของ B ยังอยู่ บันทึก Audit Log | ผลตรงทุกเงื่อนไข | ✅ |
| API-09 | ส่งคำถาม Copilot และบันทึกผล | `POST /api/copilot/chat`, symbol `AAPL`, message `แนวโน้มเป็นอย่างไร` | Status `200`, `provider: AI_Copilot_Grounded` | Status `200`, provider ถูกต้อง | ✅ |
| TC-10B | ส่ง Symbol ผิดรูปแบบใน Copilot | `symbol: "bad symbol!"` | Status `400` ก่อนเรียก Gemini | Status `400`, `status: error` | ✅ |
| TC-10C | ส่งคำถามยาวเกิน 1,000 ตัวอักษร | message ความยาว 1,001 ตัว | Status `400` ก่อนเรียก Gemini | Status `400`, `status: error` | ✅ |
| UI-10 | ปุ่มลบประวัติ Copilot เรียก DELETE | คลิก `.clear-history-btn` | เรียก `DELETE /api/copilot/history` | Endpoint และ method ผูกครบ | ✅ |
| UI-11 | ปุ่มปิด Copilot ซ่อน Modal | คลิก `#copilot-modal .modal-close` | Modal `copilot-modal` ซ่อน | `closeCopilotModal()` ผูกครบ | ✅ |
| UI-12 | ปุ่มส่งข้อความส่ง POST ไป Copilot API | คลิก `#chat-send-btn` | เรียก `POST /api/copilot/chat` | Endpoint และ method ผูกครบ | ✅ |

### 4.4.4 ฟังก์ชัน Backtest (Time Machine Modal)

| รหัส | กรณีทดสอบ | ข้อมูลนำเข้า | ผลที่คาดหวัง | ผลที่ได้รับ | ผล |
|---|---|---|---|---|:---:|
| UI-16 | ปุ่มกากบาท ปิด Time Machine Modal | คลิก `#backtest-modal .modal-close` | Modal `backtest-modal` ซ่อน | Handler ผูกครบ | ✅ |
| UI-17 | ปุ่ม "เริ่มจำลอง" เรียก Backtest API | คลิก `#backtest-modal .btn-primary` | เรียก `/api/backtest/` | `runBacktest()` และ Endpoint ผูกครบ | ✅ |
| UI-18 | ปุ่ม "ยกเลิก" ปิด Time Machine Modal | คลิก `#backtest-modal .btn-ghost` | Modal ซ่อน | `closeBacktestModal()` ผูกครบ | ✅ |

### 4.4.5 ฟังก์ชัน Change Password Modal

| รหัส | กรณีทดสอบ | ข้อมูลนำเข้า | ผลที่คาดหวัง | ผลที่ได้รับ | ผล |
|---|---|---|---|---|:---:|
| UI-13 | ปุ่มปิด Change Password ซ่อน Modal | คลิก `#password-modal .modal-close` | Modal `password-modal` ซ่อน | Handler ผูกครบ | ✅ |
| UI-14 | ปุ่มบันทึกรหัสผ่านเรียก Change Password API | คลิก `#password-modal .btn-primary` | เรียก `/api/auth/change-password` | Endpoint ผูกครบ | ✅ |
| UI-15 | ปุ่มยกเลิกซ่อน Modal | คลิก `#password-modal .btn-ghost` | Modal ซ่อน | `closePasswordModal()` ผูกครบ | ✅ |

---

## 4.5 ผลการทดสอบหน้าผู้ดูแลระบบ (Admin)

### 4.5.1 การจัดการสิทธิ์และความปลอดภัย

| รหัส | กรณีทดสอบ | ข้อมูลนำเข้า | ผลที่คาดหวัง | ผลที่ได้รับ | ผล |
|---|---|---|---|---|:---:|
| TC-11 | Member เรียก Admin API | `GET /api/admin/logs` ด้วย JWT role `member` | Status `403`, ไม่มีข้อมูล Log ถูกเปิดเผย | Status `403`, `status: error` | ✅ |
| SEC-08 | Member แก้ไขข้อมูลผู้ใช้คนอื่น (IDOR) | `PUT /api/admin/users/{victim_id}` ด้วย JWT ของ member | Status `403` | Status `403` | ✅ |
| SEC-09 | Admin ลบบัญชีตนเอง | `DELETE /api/admin/users/{admin_id}` ด้วย JWT ตัวเอง | Status `400` | Status `400`, `status: error` | ✅ |
| SEC-17 | Member เรียก Admin Endpoint ทุกตัว (10 Endpoints) | JWT role `member` กับ Admin Endpoints ทั้งหมด | Status `403` ทุก Endpoint | Status `403` ทุกกรณี | ✅ |

### 4.5.2 การจัดการข้อมูลหุ้น (Master Data)

| รหัส | กรณีทดสอบ | ข้อมูลนำเข้า | ผลที่คาดหวัง | ผลที่ได้รับ | ผล |
|---|---|---|---|---|:---:|
| TC-12A | Admin เพิ่มหุ้นใหม่และ Normalize Symbol | `POST /api/admin/stocks`, symbol = `aapl` | Status `201`, Symbol ถูก normalize เป็น `AAPL` | Status `201`, Symbol = `AAPL` | ✅ |
| TC-12B | Admin เพิ่มหุ้น Symbol ที่มีอยู่แล้ว | `POST /api/admin/stocks`, symbol `AAPL` ซ้ำ | Status `400`, `status: error` | Status `400`, `status: error` | ✅ |
| API-10 | Admin ลบหุ้นออกจากระบบ | `DELETE /api/admin/stocks/AAPL` | Status `200`, ไม่มีหุ้น `AAPL` ในฐานข้อมูล | Status `200`, ลบสำเร็จ | ✅ |
| API-13 | Admin ดึงข้อมูลหุ้นจาก Yahoo Finance | `POST /api/fetch-stock`, symbol = `aapl` | Status `200`, `new_records_added: 25` | Status `200`, จำนวนถูกต้อง | ✅ |

### 4.5.3 การจัดการผู้ใช้

| รหัส | กรณีทดสอบ | ข้อมูลนำเข้า | ผลที่คาดหวัง | ผลที่ได้รับ | ผล |
|---|---|---|---|---|:---:|
| API-11 | Admin ดูรายชื่อผู้ใช้ทั้งหมด | `GET /api/admin/users` | Status `200`, ได้ list ผู้ใช้ | Status `200`, มีชื่อผู้ใช้ที่คาด | ✅ |
| API-11 | Admin แก้ไขข้อมูลผู้ใช้ | `PUT /api/admin/users/{id}`, `first_name: "Updated"` | Status `200`, ชื่อเปลี่ยนเป็น `Updated` | Status `200`, ข้อมูลถูกต้อง | ✅ |
| API-12 | Admin ลบบัญชีผู้ใช้อื่น | `DELETE /api/admin/users/{target_id}` | Status `200`, ผู้ใช้ถูกลบออกจากฐานข้อมูล | Status `200`, ลบสำเร็จ | ✅ |

### 4.5.4 การสั่งงาน Background Tasks

| รหัส | กรณีทดสอบ | ข้อมูลนำเข้า | ผลที่คาดหวัง | ผลที่ได้รับ | ผล |
|---|---|---|---|---|:---:|
| API-14 | Admin สั่ง Scraper แบบ Background | `POST /api/admin/run-scraper` | Status `202` ทันที, เรียก `python scripts/scraper.py` | Status `202`, Subprocess ถูกเรียก | ✅ |
| API-15 | Admin สั่ง Train ทุกโมเดลแบบ Background | `POST /api/admin/train-models` | Status `202` ทันที, เรียก Script ถูกต้อง | Status `202`, Subprocess ถูกเรียก | ✅ |
| API-16 | Admin สั่ง Train แบบ Synchronous | `POST /api/admin/train-models/sync` | Status `200`, `trained: 3`, `failed: 0` | Status `200`, ผลถูกต้อง | ✅ |
| SEC-19 | Admin Task ไม่รับ Command จาก JSON Body | `POST /api/admin/run-scraper`, payload `"command": "rm -rf /"` | args ของ Subprocess คงที่ ไม่รับค่าจาก JSON | args = `['python', 'scripts/scraper.py']` เท่านั้น | ✅ |

### 4.5.5 การดู System Log

| รหัส | กรณีทดสอบ | ข้อมูลนำเข้า | ผลที่คาดหวัง | ผลที่ได้รับ | ผล |
|---|---|---|---|---|:---:|
| TC-13 | Admin กรอง Log ตาม action_type และ limit | `GET /api/admin/logs?action_type=TEST_A&limit=1` (มี Log ทั้ง TEST_A และ TEST_B) | ได้เฉพาะ `TEST_A`, จำนวน ≤ 1 รายการ | ได้ 1 รายการ, action = `TEST_A` | ✅ |
| SEC-03 | SQL Injection ใน Log Filter | `action_type=' OR 1=1 --` | ไม่เปลี่ยนเงื่อนไข Query, ได้ผลว่าง | Status `200`, data = `[]` | ✅ |

### 4.5.6 ปุ่มและ UI Controls หน้า Admin

| รหัส | กรณีทดสอบ | การกระทำ | ผลที่คาดหวัง | ผล |
|---|---|---|---|:---:|
| UI-27 | ปุ่มเมนูหน้า Admin | คลิก `#nav-toggle` | Navigation toggle | ✅ |
| UI-28 | ปุ่มเปลี่ยนรหัสผ่าน Admin | คลิก `button[onclick="openPasswordModal()"]` | Modal `password-modal` ปรากฏ | ✅ |
| UI-29 | ปุ่มออกจากระบบ (Logout) | คลิก `button[onclick="logoutAdmin()"]` | ล้าง Session, redirect ไป `login.html` | ✅ |
| UI-30 | ปุ่มรีเฟรช System Log | คลิก `button[onclick="loadLogs()"]` | เรียก `/api/admin/logs` | ✅ |
| UI-31 | ปุ่มเพิ่มหุ้น | คลิก `button[onclick="addStock()"]` | เรียก `POST /api/admin/stocks` | ✅ |
| UI-32 | ปุ่มดึงข้อมูลตลาด (Scraper) | คลิก `button[onclick="runTask('run-scraper')"]` | เรียก `/api/admin/` | ✅ |
| UI-33 | ปุ่มเทรนโมเดล Prophet | คลิก `button[onclick="trainModels()"]` | เรียก `train-models` | ✅ |
| UI-34 | ปุ่มรีเฟรชรายชื่อผู้ใช้ | คลิก `button[onclick="loadUsers()"]` | เรียก `/api/admin/users` | ✅ |
| UI-35 | ปุ่มปิด User Edit Modal | คลิก `#user-edit-modal .modal-close` | Modal ซ่อน | ✅ |
| UI-36 | ปุ่มบันทึก User Edit | คลิก `#user-edit-modal .btn-primary` | เรียก `PUT /api/admin/users/` | ✅ |
| UI-37 | ปุ่มยกเลิก User Edit | คลิก `#user-edit-modal .btn-ghost` | Modal ซ่อน | ✅ |
| UI-38 | ปุ่มปิด Password Modal Admin | คลิก `#password-modal .modal-close` | Modal ซ่อน | ✅ |
| UI-39 | ปุ่มบันทึกรหัสผ่าน Admin | คลิก `#password-modal .btn-primary` | เรียก `/api/auth/change-password` | ✅ |
| UI-40 | ปุ่มยกเลิกรหัสผ่าน Admin | คลิก `#password-modal .btn-ghost` | Modal ซ่อน | ✅ |
| UI-42 | ปุ่มลบ/แก้ไข ใน Dynamic Table ไม่ฝัง User Data ใน onclick | ตรวจ HTML/JS ของ `admin.html` | ใช้ `data-action` แทน inline onclick | ✅ |
| UI-43 | ข้อมูลผู้ใช้และหุ้นถูก Encode ก่อนแสดงผล | ตรวจ JS ของ `admin.html` | มี `escapeAdminHtml()` และ `textContent` | ✅ |

---

## 4.6 ผลการทดสอบ OTP รีเซ็ตรหัสผ่าน (Forgot Password Flow)

| รหัส | กรณีทดสอบ | ข้อมูลนำเข้า | ผลที่คาดหวัง | ผลที่ได้รับ | ผล |
|---|---|---|---|---|:---:|
| API-04 | ใช้ OTP ถูกต้องเปลี่ยนรหัสผ่าน (ครั้งที่ 1) | OTP `123456`, รหัสใหม่ `ChangedPass2` | Status `200`, Login ด้วยรหัสใหม่ได้ | Status `200`, Login สำเร็จ | ✅ |
| API-04 | ใช้ OTP เดิมซ้ำ (ครั้งที่ 2) | OTP เดิม `123456` | Status `400` (OTP ใช้แล้ว) | Status `400` | ✅ |
| SEC-11 | Forgot Password ไม่เปิดเผยว่ามีบัญชีหรือไม่ | อีเมลที่มีในระบบ vs ไม่มี | ข้อความ Response เหมือนกัน, Status `200` ทั้งคู่ | ข้อความ Response เหมือนกัน | ✅ |

---

## 4.7 ผลการทดสอบข้ามหน้า (Global UI)

| รหัส | กรณีทดสอบ | ข้อมูลนำเข้า | ผลที่คาดหวัง | ผลที่ได้รับ | ผล |
|---|---|---|---|---|:---:|
| UI-41 | ปุ่มทุกตัวมี `type` และชื่อที่อ่านได้ (Accessibility) | ทุกปุ่มใน 4 หน้า (index, login, register, admin) | `type` เป็น `button` หรือ `submit`, มี text หรือ `aria-label` | ปุ่มทุกตัวผ่านเกณฑ์ | ✅ |
| TC-01 | API ส่ง Security Headers พื้นฐาน | `GET /` | `X-Content-Type-Options`, `X-Frame-Options` | Headers ครบ | ✅ |
| SEC-13 | API ส่ง Content Security Policy | `GET /` | `Content-Security-Policy` Header ครบ directive | Header ครบ | ✅ |
| SEC-15 | Production ปฏิเสธ Secret ที่สั้น | Config `SECRET_KEY: "short"` ใน debug=False | Raise `RuntimeError` | `RuntimeError` ถูก raise | ✅ |
| SEC-16 | รหัสผ่านถูก Hash ด้วย scrypt | สมัครสมาชิกแล้วดู field `password_hash` | ขึ้นต้นด้วย `scrypt:` ไม่ใช่ plaintext | `scrypt:...` ถูกต้อง | ✅ |
| API-01 | Auth Config ไม่เปิดเผย Secret | `GET /api/auth/config` | ได้เฉพาะ `google_client_id` และ `google_login_enabled` | Fields ถูกต้อง ไม่มี `secret` | ✅ |
| API-02 | ฐานข้อมูลเชื่อมต่อได้ | `GET /test-db` | Status `200`, `status: success` | Status `200` | ✅ |
| API-05 | Google Login ปฏิเสธ Request ไม่มี Credential | `POST /api/auth/google`, body ว่าง | Status `400`, `status: error` | Status `400` | ✅ |

---

## 4.8 สรุปผลการทดสอบ

ระบบ TradeSensei ผ่านการทดสอบแบบ Black Box ครบทั้ง **120 กรณีทดสอบ (ร้อยละ 100)** ครอบคลุมทุกหน้าเว็บและทุก API Endpoint โดยไม่พบกรณีที่ไม่ผ่านแม้แต่กรณีเดียว ทั้งในด้านฟังก์ชันการทำงาน ความปลอดภัย (OWASP) และการเชื่อมต่อปุ่มกับ Endpoint ที่ถูกต้อง
