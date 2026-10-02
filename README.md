# TradeSensei — AI-Powered Stock Market Analysis & Forecasting Platform

**TradeSensei** เป็นเว็บแอปพลิเคชันสนับสนุนการวิเคราะห์และทำนายราคาหุ้นด้วยปัญญาประดิษฐ์ (Market Intelligence & Stock Analysis Platform) ที่ผสานรวมโมเดลอนุกรมเวลา (Time-Series Forecasting), การประมวลผลภาษาธรรมชาติ (NLP Sentiment Analysis) และสถาปัตยกรรม Retrieval-Augmented Generation (RAG) เข้าด้วยกันในพื้นที่ทำงานเดียว

---

## ศูนย์รวมเอกสารโครงการ (Project Documentation Index)

| ลำดับ | รายชื่อเอกสาร | เนื้อหาและขอบเขตเอกสาร | ลิงก์เข้าถึงเอกสาร |
|---|---|---|---|
| 0 | **บทคัดย่อโครงการ (Project Abstract)** | บทคัดย่อทั้งภาษาไทยและภาษาอังกฤษ ตามรูปแบบโครงสร้างบทคัดย่อปริญญานิพนธ์ | [ABSTRACT.md](file:///c:/Users/reiji/Desktop/trade_sensei/ABSTRACT.md) |
| 1 | **เอกสารรวมทฤษฎีและหลักการ (Theories & Fundamentals)** | รวมสมการคณิตศาสตร์ (Prophet GAM, Log Scale), โมเดล NLP TextBlob, สถาปัตยกรรม RAG + Gemini, ทฤษฎีการเงิน Time Machine และหลักการความปลอดภัยไซเบอร์ | [THEORY.md](file:///c:/Users/reiji/Desktop/trade_sensei/THEORY.md) |
| 2 | **รายงานผลการพัฒนาระบบ (Chapter 4 Report)** | รายงานผลการดำเนินงาน การทดสอบฟังก์ชัน Black Box และผลการทดสอบระบบ 120 กรณีทดสอบ (Pass Rate 100%) | [CHAPTER_4.md](file:///c:/Users/reiji/Desktop/trade_sensei/CHAPTER_4.md) |
| 3 | **รายละเอียดกรณีทดสอบ (Test Case Specifications)** | รายละเอียดชุดทดสอบอัตโนมัติด้วย `pytest` แยกตามหมวด Core Acceptance (`TC-*`), Features (`API-*`), Security (`SEC-*`) และ UI Controls (`UI-*`) | [TEST_CASES.md](file:///c:/Users/reiji/Desktop/trade_sensei/TEST_CASES.md) |
| 4 | **คู่มือความปลอดภัย (Security Policy)** | ข้อกำหนด Environment Variables, การตั้งค่า Google OAuth, ระบบแฮชรหัสผ่าน `scrypt`, OTP Policy และ Hardening Checklist | [SECURITY.md](file:///c:/Users/reiji/Desktop/trade_sensei/SECURITY.md) |
| 5 | **สคริปต์และกฎของ AI Copilot (AI Rules & Persona)** | ข้อกำหนดบทบาทสมมติ (Sensei Persona), กฎเหล็ก 5 ข้อ, สถาปัตยกรรมการสื่อสารเสมือนมนุษย์ และการแปลผลให้เข้าใจง่าย | [docs/COPILOT_AI_RULES.md](file:///c:/Users/reiji/Desktop/trade_sensei/docs/COPILOT_AI_RULES.md) |
| 6 | **ภาคผนวก ก: คู่มือการติดตั้งและกำหนดค่าระบบ (Installation & Config Guide)** | คู่มือการติดตั้งสภาพแวดล้อม Docker, ฐานข้อมูล, การตั้งค่าคีย์ API, Cloudflare Tunnel และการนำขึ้น Web Hosting | [INSTALLATION_MANUAL.md](file:///c:/Users/reiji/Desktop/trade_sensei/INSTALLATION_MANUAL.md) |
| 7 | **ภาคผนวก ข: คู่มือการใช้งานระบบ (User & Admin Manual)** | คู่มือการใช้งานสำหรับสมาชิก ผู้ใช้ทั่วไป และผู้ดูแลระบบ ครอบคลุมทุกหน้าจอ สำหรับนำเข้าเอกสารโครงงาน | [USER_MANUAL.md](file:///c:/Users/reiji/Desktop/trade_sensei/USER_MANUAL.md) |

---

## ฟีเจอร์หลักของระบบ (Key Capabilities)

* **Interactive Candlestick & Crisp Trendlines:** ติดตามข้อมูลราคา OHLCV ย้อนหลัง 2 ปี กราฟปฏิสัมพันธ์ด้วย Plotly.js พร้อมเส้นแนวโน้ม SMA 20 และ SMA 50 แบบ Linear คมชัด หนักแน่น ตรงตามมาตรฐานสากล
* **Comprehensive Market Catalog (29 Assets):** ครอบคลุมหุ้นไทย SET50 ชั้นนำ (PTT, AOT, DELTA, ADVANC, CPALL, KBANK, SCB, BDMS, GULF, SCC, TRUE, MINT, PTTEP, BBL, CPN, BH), หุ้นเทคโนโลยีระดับโลก (AAPL, MSFT, TSLA, NVDA, GOOGL, AMZN, META, AMD, NFLX) และคริปโทเคอร์เรนซี (BTC, ETH, SOL, BNB)
* **AI 7-Day Price Forecast:** พยากรณ์ราคาปิด 7 วันล่วงหน้าและขอบเขตความเชื่อมั่น 90% ด้วยโมเดล Prophet (Piecewise Linear GAM) พร้อมการประเมินค่าความแม่นยำ (Hold-out Accuracy %)
* **AI News Sentiment Analysis:** วิเคราะห์อารมณ์ข่าวการเงินด้วย TextBlob NLP แสดงคะแนน Polarity Score (-1 ถึง +1) และสัดส่วนข่าวบวก/ลบ
* **Sensei Copilot (Human-Friendly RAG Chatbot):** ผู้ช่วยวิเคราะห์การลงทุนที่แทนตัวเองว่า "ผม" สื่อสารเสมือนมนุษย์ อบอุ่น เป็นมิตร อธิบายตัวเลขเชิงลึกให้เข้าใจง่าย ไม่ใส่รหัสอ้างอิงเอกสาร พร้อมไฮไลท์ข้อความสีเขียวสำหรับสัญญาณแนะนำ/เชิงบวก และสีแดงสำหรับสัญญาณระมัดระวัง/ไม่แนะนำ
* **Time Machine Investment Simulation:** จำลองผลตอบแทนการลงทุนในอดีต (1–24 เดือน) เปรียบเทียบกับอัตราดอกเบี้ยเงินฝากออมทรัพย์ 2.5% ต่อปี พร้อม UI สะอาดตา
* **Secure Authentication & Recovery:** รองรับระบบสมาชิก, เข้าสู่ระบบด้วย Google Sign-In พร้อมโหมด Demo Member และระบบขอรหัสผ่านใหม่ (Forgot Password) ผ่านอีเมล OTP (Resend)
* **Admin System Management:** หน้าบริหารจัดการสมาชิก รายชื่อหุ้น สั่ง Batch Scrape สั่งเทรนโมเดล และตรวจสอบ System Logs

---

## เทคโนโลยีที่ใช้ (Tech Stack)

* **Frontend:** HTML5, Vanilla JavaScript (ES6+), Vanilla CSS (Custom Design System), Plotly.js (No React/Vite/Next.js)
* **Backend:** Python 3.10+, Flask RESTful Framework, Flask-JWT-Extended, Flask-SQLAlchemy (MVC Architecture)
* **Database:** PostgreSQL 15 (Production / Docker), SQLite (Isolated Automated Testing)
* **AI / Machine Learning:** Facebook Prophet (Meta), TextBlob (NLP), Google Gemini 2.5/1.5 Flash (Generative AI)
* **Infrastructure & Security:** Docker Compose, Werkzeug scrypt Hashing, Resend Email API, Pytest (120 Automated Tests)

---

## วิธีการติดตั้งและรันระบบ (Quick Start)

### 1. การรันด้วย Docker Compose

```bash
# คัดลอกไฟล์คอนฟิก
cp .env.example .env

# สั่งเริ่มต้นบริการ Backend และ Database
docker compose up -d --build
```

เข้าใช้งานผ่านเว็บเบราว์เซอร์:
* **Frontend:** `http://localhost:5500/index.html` (รันผ่าน `python -m http.server 5500` ในโฟลเดอร์ `frontend/`)
* **Backend API Health Check:** `http://localhost:5000/api/health`

### 2. การรันชุดทดสอบอัตโนมัติ (Automated Testing)

```bash
docker compose exec backend pytest -q
```
*ผลลัพธ์การทดสอบ: ผ่านครบทั้งหมด 120 กรณีทดสอบ (100% Pass Rate)*

---

*โครงการ TradeSensei — พัฒนาเพื่อการศึกษาและวิเคราะห์ข้อมูลการลงทุน*
