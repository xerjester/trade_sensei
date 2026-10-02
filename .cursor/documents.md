# 📘 Project Specification Document (เอกสารข้อกำหนดโครงงาน)
**Project Name:** Stock Prediction Support System with Artificial Intelligence (ระบบสนับสนุนการทำนายหุ้นด้วยปัญญาประดิษฐ์ - TradeSensei)
**Document Type:** Vibe Coding Context / System Requirements Specification

เอกสารฉบับนี้สรุปขอบเขตและข้อกำหนดทางเทคนิคทั้งหมดจากโครงงานวิจัย เพื่อใช้เป็น Context ให้กับ AI Assistant (เช่น Cursor, Copilot, Windsurf) ในการพัฒนาโค้ดให้ตรงตามโครงสร้างและสถาปัตยกรรมที่ออกแบบไว้

---

## 🛠 1. Technology Stack (เครื่องมือและเทคโนโลยี)
ระบบนี้ได้รับการออกแบบให้ทำงานแบบผสมผสาน (Hybrid AI Architecture) โดยมี Tech Stack ดังนี้:
* **Frontend:** HTML5, CSS3, JavaScript (Vanilla), **Plotly.js** (สำหรับกราฟ OHLC/Candlestick)
* **Backend:** Python (Flask Framework)
* **Database:** PostgreSQL (ใช้ฟีเจอร์ระดับ Enterprise เช่น JSONB)
* **AI & Machine Learning:**
    * **Time Series Forecasting:** Facebook Prophet (ทำนายราคาล่วงหน้า 7 วัน)
    * **NLP / Sentiment Analysis:** TextBlob (ประมวลผลอารมณ์ข่าวสาร Offline)
    * **AI Copilot (RAG):** Gemini API (วิเคราะห์ร่วมกับกราฟและข่าว เพื่อโต้ตอบด้วยภาษาธรรมชาติ)
* **Data Processing:** Pandas, NumPy
* **Data Source:** Yahoo Finance API (yfinance) ดึงข้อมูล Daily OHLCV ย้อนหลัง 2 ปี
* **DevOps:** Docker (Containerization สำหรับ PostgreSQL และ Environment)

---

## 👥 2. User Roles & Features (ขอบเขตผู้ใช้งาน)

### 2.1 Guest (ผู้ใช้งานทั่วไป)
* **Dashboard:** ดูภาพรวมและรายชื่อหุ้นทั้งหมด (SET, NASDAQ, Crypto)
* **Sector Filter:** คัดกรองหุ้นตามหมวดหมู่ธุรกิจ
* **Interactive Chart:** ดูกราฟราคาหุ้นย้อนหลังผ่าน Plotly.js
* **News Integration:** เข้าถึงลิงก์ข่าวสารที่เกี่ยวข้องกับหุ้นแต่ละตัว

### 2.2 Member (สมาชิก)
* **Authentication:** ระบบสมัครสมาชิกและเข้าสู่ระบบ
* **AI Prediction Chart:** ดูกราฟพยากรณ์ราคาล่วงหน้า 7 วัน (เชื่อมรอยต่อกับวันหยุดทำการอัตโนมัติ)
* **On-Demand Prediction:** สั่งประมวลผลทำนายราคา ณ เวลานั้นได้ทันที
* **Deep Analysis:** ดูองค์ประกอบแนวโน้ม (Trend Components, Seasonality) และรายละเอียดอารมณ์ข่าว (Sentiment Breakdown)
* **Time Machine Backtest:** ฟีเจอร์จำลองผลตอบแทนการลงทุนย้อนหลัง (กำไร/ขาดทุน เทียบกับอัตราดอกเบี้ยเงินฝาก)
* **Sensei Copilot (AI Chatbot):** ผู้ช่วยแชทบอทวิเคราะห์สถานะหุ้นแบบธรรมชาติ (RAG System)

### 2.3 Administrator (ผู้ดูแลระบบ)
* **Master Data Management:** เพิ่ม/ลบ/แก้ไข รายชื่อหุ้นและหมวดหมู่ในฐานข้อมูล
* **Data Scraper:** สั่งดึงข้อมูลราคาหุ้นย้อนหลัง EOD จาก Yahoo Finance ลงฐานข้อมูลอัตโนมัติ
* **Batch Processing:** สั่งเทรนโมเดล AI (Prophet) ให้เรียนรู้และอัปเดตหุ้นทุกตัวในระบบ
* **System Logs:** ตรวจสอบสถานะการทำงาน ข้อผิดพลาด และประวัติการรันผ่าน Terminal

---

## 🗄️ 3. Database Architecture (สถาปัตยกรรมฐานข้อมูล)
ระบบประกอบด้วย 10 ตารางหลัก (อ้างอิงจาก ER Diagram):
1.  `users`: เก็บข้อมูลสมาชิก รหัสผ่านที่เข้ารหัส และสิทธิ์ (member/admin)
2.  `stocks`: เก็บข้อมูล Master หุ้น (Symbol, Company, Category)
3.  `user_favorites`: Mapping หุ้นที่สมาชิกกดถูกใจ
4.  `historical_prices`: ข้อมูลราคาย้อนหลัง OHLCV (ดึงมา 2 ปี)
5.  `price_predictions`: ผลการทำนายราคา yhat, yhat_lower, yhat_upper ล่วงหน้า 7 วัน
6.  `news`: ข้อมูลข่าวสารและลิงก์ภายนอก
7.  `news_sentiments`: ผลการวิเคราะห์อารมณ์ (Positive/Neutral/Negative) และคะแนนจาก TextBlob
8.  `system_logs`: เก็บประวัติการกดสั่ง Scrape/Train ของ Admin
9.  `chat_history`: เก็บประวัติการคุยกับ AI Copilot
10. `stock_models`: เก็บค่า Parameter/JSON ของโมเดลที่เทรนแล้ว

---

## ⚙️ 4. System Workflow (กระบวนการทำงานหลัก)

### 4.1 Data Pipeline (Scrape & Train)
1.  **Admin Trigger:** Admin กดสั่ง "Scrape Data"
2.  **Fetch & Clean:** ระบบเรียกใช้ `yfinance` ดึงข้อมูลดิบมาลบค่า Null/NA ปรับ Format
3.  **Store:** บันทึกลงตาราง `historical_prices`
4.  **Admin Trigger:** Admin กดสั่ง "Train Models"
5.  **Predict:** ระบบรันโมเดล Prophet ทยอยพยากรณ์ราคาล่วงหน้า 7 วัน
6.  **Store Output:** บันทึกผลลง `price_predictions` และ `stock_models`

### 4.2 NLP & Copilot Pipeline (RAG System)
1.  **Scrape News:** ดึงข่าวล่าลุด ตัด HTML tags / Stop words
2.  **Sentiment:** ส่งผ่าน TextBlob วิเคราะห์ Polarity Score และเก็บลงตาราง
3.  **User Query:** สมาชิกพิมพ์ถามในหน้ากราฟหุ้น เช่น "แนวโน้มหุ้นนี้เป็นยังไง"
4.  **RAG Context:** ระบบหลังบ้านดึงข้อมูลราคาปัจจุบัน (D3), ข่าวอารมณ์ (D4), ผลทำนาย Prophet (D5) และประวัติแชทเดิม (D6) ยัดเป็น Context
5.  **LLM Generation:** ส่ง Context ไปให้ Gemini API ประมวลผลและตอบกลับเป็นภาษาธรรมชาติ

---
**Note to AI Assistant:** When generating code based on this document, strictly adhere to the Vanilla HTML/JS frontend and Python Flask backend. Do NOT hallucinate features outside this scope. Pay special attention to the RAG context building for the Copilot feature.