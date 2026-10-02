# เอกสารรวมทฤษฎีและหลักการทางวิทยาการคำนวณที่ใช้ในโครงการ TradeSensei (Project Theories & Fundamentals)

เอกสารฉบับนี้รวบรวมทฤษฎี โมเดลคณิตศาสตร์ หลักการทางวิศวกรรมซอฟต์แวร์ สถาปัตยกรรมปัญญาประดิษฐ์ และหลักการความปลอดภัยไซเบอร์ทั้งหมดที่ถูกประยุกต์ใช้ในการพัฒนาระบบสนับสนุนการทำนายและวิเคราะห์หุ้น **TradeSensei**

---

## 1. ทฤษฎีการทำนายอนุกรมเวลาและคณิตศาสตร์ (Time-Series Forecasting & Applied Mathematics)

ระบบทำนายราคาหุ้น 7 วันล่วงหน้าของ TradeSensei ประยุกต์ใช้โมเดลอนุกรมเวลาเชิงสถิติขั้นสูงเพื่อวิเคราะห์พฤติกรรมราคาในอดีต

### 1.1 Prophet Generalized Additive Model (GAM)
ระบบใช้โมเดล **Prophet** (พัฒนาโดย Meta/Facebook) ซึ่งอ้างอิงโครงสร้าง **Generalized Additive Model (GAM)** ในรูปแบบการย่อยสลายอนุกรมเวลา (Time-Series Decomposition) ดังสมการ:

$$y(t) = g(t) + s(t) + h(t) + \epsilon_t$$

โดยที่:
* **$g(t)$ — Growth Trend (แนวโน้มหลัก):** คำนวณแบบ Piecewise Linear Model ที่รองรับจุดเปลี่ยนแนวโน้ม (Changepoints)
  $$g(t) = (k + a(t)^T \delta) t + (m + a(t)^T \gamma)$$
  - ค่า `changepoints` ถูกควบคุมด้วย `changepoint_prior_scale = 0.08` เพื่อป้องกันปัญหา Overfitting จากความผันผวนระยะสั้น
* **$s(t)$ — Seasonality (ฤดูกาล):** ในระบบกำหนดให้เป็นแบบ **Multiplicative Seasonality** ($y(t) = g(t) \cdot (1 + s(t))$) เพื่อให้ขนาดของฤดูกาลปรับตามระดับราคาหุ้น
  - ใช้ **Fourier Series** ในการจำลองฤดูกาลรายสัปดาห์ (Weekly Seasonality) และรายปี (Yearly Seasonality เมื่อข้อมูลมีตั้งแต่ 252 วันทำการขึ้นไป)
  - ปรับค่า `seasonality_prior_scale = 5.0`
* **$h(t)$ — Holiday Effects:** ผลกระทบจากวันหยุดนักขัตฤกษ์
* **$\epsilon_t$ — Error Term:** ค่าความคลาดเคลื่อนที่มีการแจกแจงแบบปกติ (Normally Distributed Error)

### 1.2 การประเมินช่วงความเชื่อมั่น (Uncertainty Interval)
* ระบบคำนวณช่วงความเชื่อมั่นการทำนายราคา (Predicted Lower Bound & Predicted Upper Bound) ที่ระดับความเชื่อมั่น 90% (`interval_width = 0.90`)
* ใช้เทคนิคการสุ่มตัวอย่าง **Bayesian Monte Carlo Sampling** จำนวน 500 ตัวอย่าง (`uncertainty_samples = 500`) เพื่อประเมินความไม่แน่นอนของแนวโน้มราคา

### 1.3 การแปลงสเกลข้อมูลราคา (Logarithmic Scale Transformation)
เพื่อจัดการความผันผวนของราคาหุ้นที่มีสเกลต่างกันมาก (เช่น หุ้นราคาหลักบาทเทียบกับหลักพันบาท หรือ Cryptocurrencies) และป้องกันไม่ให้โมเดลทำนายราคาติดลบ ระบบใช้การแปลงสเกลแบบลอการิทึม:

1. **Forward Transformation:**
   $$y_{\text{trans}} = \ln(1 + \text{Close}) = \text{log1p}(\text{Close})$$
2. **Inverse Transformation (คำนวณราคาสุทธิกลับ):**
   $$\hat{y} = \max(0, e^{yhat} - 1) = \max(0, \text{expm1}(yhat))$$

### 1.4 การตรวจสอบความถี่ของตลาดอัตโนมัติ (Market Frequency Inference)
ระบบตรวจจับประเภทสินทรัพย์เพื่อกำหนดความถี่ในการพยากรณ์:
* **Business Days ('B'):** สำหรับหุ้นในตลาดหลักทรัพย์ (เช่น SET, NASDAQ, NYSE) ที่มีการซื้อขายเฉพาะวันทำการจันทร์–ศุกร์
* **Calendar Days ('D'):** สำหรับสินทรัพย์ที่ทำการซื้อขายตลอด 24/7 (เช่น Cryptocurrencies: BTC-USD, ETH-USD)

### 1.5 ทฤษฎีการประเมินความแม่นยำโมเดล (Model Validation & Loss Metrics)
ระบบใช้เทคนิค **Hold-out Validation** โดยแบ่งข้อมูลล่าสุด 14 วัน (Hold-out dataset) ออกมาทดสอบโดยไม่ให้โมเดลเห็นขณะฝึกสอน เพื่อคำนวณตัววัดประสิทธิภาพ:

* **Mean Absolute Error (MAE):** ความคลาดเคลื่อนสัมบูรณ์เฉลี่ยในหน่วยราคาสินทรัพย์
  $$\text{MAE} = \frac{1}{n} \sum_{i=1}^{n} |y_i - \hat{y}_i|$$
* **Mean Absolute Percentage Error (MAPE):** ความคลาดเคลื่อนสัมบูรณ์เฉลี่ยคิดเป็นเปอร์เซ็นต์
  $$\text{MAPE} = \frac{100\%}{n} \sum_{i=1}^{n} \left| \frac{y_i - \hat{y}_i}{y_i} \right|$$
* **Model Accuracy Percentage:** ดัชนีความแม่นยำที่แปลงให้อยู่บนสเกล 0–100% สำหรับแสดงผลในแดชบอร์ด
  $$\text{Accuracy \%} = \max(0, \min(100, 100 - \text{MAPE}))$$

---

## 2. ทฤษฎีการประมวลผลภาษาธรรมชาติและการวิเคราะห์อารมณ์ข่าว (NLP & Sentiment Analysis)

### 2.1 Lexicon-based & Rule-based Natural Language Processing
ระบบวิเคราะห์แนวโน้มอารมณ์จากหัวข้อข่าวและเนื้อหาข่าวการเงินด้วยไลบรารี **TextBlob** ซึ่งใช้วิธีการทาง Lexicon (คลังคำศัพท์ระบุค่าน้ำหนัก) ร่วมกับกฎไวยากรณ์ (Rule-based Rules):

* **Polarity Score ($S_{\text{polarity}}$):** ให้ค่าอยู่ในช่วง $[-1.0, +1.0]$
  - $-1.0$: อารมณ์เชิงลบอย่างรุนแรง (Extremely Negative)
  - $0.0$: อารมณ์เป็นกลาง (Neutral)
  - $+1.0$: อารมณ์เชิงบวกอย่างรุนแรง (Extremely Positive)

### 2.2 การจัดกลุ่มอารมณ์ข่าว (Sentiment Decision Thresholds)
ระบบแบ่งเกณฑ์การตัดสินอารมณ์ข่าวออกเป็น 3 กลุ่มดังนี้:

$$\text{Sentiment Label} = \begin{cases} \text{Positive} & \text{if } S_{\text{polarity}} > +0.1 \\ \text{Negative} & \text{if } S_{\text{polarity}} < -0.1 \\ \text{Neutral} & \text{if } -0.1 \le S_{\text{polarity}} \le +0.1 \end{cases}$$

### 2.3 การรวมผลอารมณ์ข่าวเชิงสถิติ (Sentiment Aggregation)
คำนวณค่าเฉลี่ยถ่วงน้ำหนักอารมณ์ข่าวล่าสุด 10 รายการเพื่อใช้ประเมินภาพรวม (Overall Sentiment Score) ของหุ้นตัวนั้นๆ

---

## 3. สถาปัตยกรรมโมเดลภาษาขนาดใหญ่และการค้นคืนข้อมูล (LLM Architecture & RAG)

### 3.1 Retrieval-Augmented Generation (RAG)
ระบบ **Sensei Copilot** ทำงานตามแนวคิด **RAG Architecture** เพื่อป้องกันปัญหาการสร้างข้อมูลเท็จ (Hallucination) ของ AI โดยแบ่งกระบวนการเป็น 3 ขั้นตอน:

1. **Retrieval (การค้นคืนข้อมูล):** ดึงข้อมูลจริงจากฐานข้อมูลภายในระบบตาม Data Store ดังนี้:
   - **D2:** ข้อมูลบริษัทและประเภทสินทรัพย์
   - **D3:** ราคาปิดย้อนหลังล่าสุด
   - **D4:** สรุปอารมณ์ข่าวและหัวข้อข่าวล่าสุด
   - **D5:** ผลการทำนายราคาและองค์ประกอบแนวโน้ม 7 วันจาก Prophet
2. **Context Construction (การสร้างบริบทข้อเท็จจริง):** รวบรวมข้อมูลเป็น FACT Block เพื่อป้อนเข้าสู่ Prompt
3. **Grounded Generation (การสร้างคำตอบภายใต้กรอบข้อมูล):** กำหนดให้ LLM เรียบเรียงคำตอบเฉพาะจาก FACT Block เท่านั้น

### 3.2 Prompt Engineering & Strict Output Constraints
* **Temperature Control:** กำหนด `temperature = 0.1` เพื่อเน้นคำตอบที่แน่นอน เที่ยงตรง ไม่เพ้อฝัน
* **Structured Response Enforcement:** กำหนดให้ Gemini คืนค่าในรูปแบบ **JSON Schema** เท่านั้น (`response_mime_type = "application/json"`)
* **Fact Citation Verification:** บังคับให้ระบบระบุแหล่งอ้างอิง (Citations) เฉพาะที่มาจาก D2, D3, D4, D5 เท่านั้น

### 3.3 Fail-Closed Fallback Pattern
กรณีที่ Gemini API ไม่สามารถใช้งานได้ หรือสร้างผลลัพธ์ที่ไม่อยู่ในรูปแบบ JSON ตามกำหนด ระบบจะสลับไปใช้ **Deterministic Rule-Based Generator** อัตโนมัติ เพื่อดึงข้อมูลจริงจากฐานข้อมูลมาแสดงผลโดยตรง ทำให้ระบบทำงานได้อย่างต่อเนื่อง 100%

---

## 4. ทฤษฎีการเงินและการจำลองการลงทุน (Financial Theory & Portfolio Simulation)

### 4.1 การจำลองผลตอบแทนย้อนหลัง (Time Machine Backtesting)
ระบบจำลองการลงทุนโดยคำนวณผลตอบแทนจากราคาซื้อขายจริงตามช่วงเวลาในอดีต (1–24 เดือน):

1. **จำนวนหุ้นที่ซื้อได้ (Share Allocation):**
   $$\text{Shares} = \frac{\text{Initial Amount}}{\text{Start Close Price}}$$
2. **มูลค่าพอร์ต ณ วันสิ้นสุด (Final Portfolio Value):**
   $$\text{Final Value} = \text{Shares} \times \text{End Close Price}$$
3. **อัตราผลตอบแทนของหุ้น (Stock ROI):**
   $$\text{Stock Return \%} = \left( \frac{\text{Final Value} - \text{Initial Amount}}{\text{Initial Amount}} \right) \times 100$$

### 4.2 การเปรียบเทียบกับเกณฑ์มาตรฐานอัตราดอกเบี้ยปลอดความเสี่ยง (Benchmark Comparison)
ใช้ทฤษฎีดอกเบี้ยทบต้น (Compound Interest Formula) คำนวณผลตอบแทนจากการฝากเงินตามอัตราดอกเบี้ยออมทรัพย์ขั้นต่ำ (Risk-Free Rate / Fixed Deposit Benchmark = 2.5% ต่อปี):

$$\text{Deposit Final Value} = \text{Initial Amount} \times (1 + r)^{\frac{d}{365}}$$

โดยที่:
* $r = 0.025$ (อัตราดอกเบี้ยเงินฝาก 2.5% ต่อปี)
* $d$ = จำนวนวันถือครองสินทรัพย์ (Days Held)

---

## 5. สถาปัตยกรรมระบบและวิศวกรรมซอฟต์แวร์ (System Architecture & Software Engineering)

### 5.1 Data Flow Diagram (DFD) Architecture
โครงสร้างระบบออกแบบตามลำดับการไหลของข้อมูล (DFD Level 1.0 – 5.0) ร่วมกับคลังข้อมูล (Data Stores):

```
+-----------------------------------------------------------------------+
|                            DATA STORES                                |
+-----------------------------------------------------------------------+
| [D1] Users             - ข้อมูลสมาชิก สิทธิ์ และ Password Hash        |
| [D2] Stocks            - รายชื่อหุ้น และสัญลักษณ์สินทรัพย์             |
| [D3] HistoricalPrices  - ข้อมูลราคาย้อนหลัง OHLCV                    |
| [D4] News & Sentiments - ข่าวสารและผลวิเคราะห์อารมณ์ข่าว              |
| [D5] Forecasts & Models- ผลทำนายราคา 7 วัน และ Artifacts โมเดล       |
| [D6] ChatHistory       - ประวัติการสนทนาระหว่างสมาชิกและ Copilot       |
| [D7] SystemLogs        - บันทึกการทำงานและการตรวจสอบระบบ             |
+-----------------------------------------------------------------------+
```

### 5.2 Layered Architectural Pattern (Router-Service-Repository Pattern)
ระบบแยกส่วนความรับผิดชอบ (Separation of Concerns) ออกเป็นชั้นชัดเจน:
* **Presentation Layer (Frontend):** Vanilla HTML5 / JavaScript (ES6+) / Plotly.js สำหรับกราฟปฏิสัมพันธ์
* **Routing / Controller Layer (`app/routers/`):** จัดการ HTTP Requests, JWT Validation, Response Formatting
* **Business Logic / Service Layer (`app/services/`):** คำนวณผลทางคณิตศาสตร์, ประมวลผล ML/NLP, จัดการ RAG
* **Data Access / Repository Layer (`app/models/`):** SQLAlchemy ORM เชื่อมต่อและจัดการฐานข้อมูล PostgreSQL

### 5.3 Asynchronous Pipeline & Data Ingestion ETL Pattern
* **Extract:** ดึงข้อมูลราคาย้อนหลัง OHLCV และข่าวสารผ่าน Yahoo Finance API (`yfinance`) พร้อมระบบสำรองผ่าน Yahoo Finance RSS Parser (`BeautifulSoup4`)
* **Transform:** ทำความสะอาดข้อมูล (Data Cleaning), ลบค่าสูญหาย (NaN/Null Imputation), แปลงเขตเวลา (Timezone Normalization)
* **Load:** บันทึกลงฐานข้อมูล PostgreSQL พร้อมเรียกกระบวนการ NLP Sentiment Analysis แบบอัตโนมัติ

---

## 6. ทฤษฎีความปลอดภัยของเว็บแอปพลิเคชันและการเข้ารหัสลับ (Cybersecurity & Cryptography)

### 6.1 Authentication & Authorization
* **Stateless Authentication (JWT):** ใช้ JSON Web Token ในการยืนยันตัวตน กำหนดอายุการใช้งาน Token และส่งผ่าน Authorization Header (`Bearer Token`)
* **Role-Based Access Control (RBAC):** กำหนดสิทธิ์การเข้าถึงทรัพยากรแบ่งเป็น `guest`, `member`, และ `admin` โดยมี Custom Decorator (`@admin_required`) ในการตรวจสอบสิทธิ์สม่ำเสมอ
* **OAuth 2.0 Identity Federation:** รองรับการเข้าสู่ระบบผ่าน Google OAuth 2.0 โดยตรวจสอบ Token และซิงค์ข้อมูลผู้ใช้ปลอดภัย

### 6.2 Cryptography & Data Protection
* **Password Hashing (scrypt KDF):** เข้ารหัสผ่านด้วยฟังก์ชันถอดรหัสรหัสผ่าน **scrypt** (Key Derivation Function) ซึ่งทนทานต่อการโจมตีแบบ Brute-force และ GPU Cracking
* **One-Time Password (OTP) Cryptography:**
  - สร้างรหัส OTP 6 หลักโดยใช้การสุ่มตัวอย่างระดับ Cryptographic Randomness (`secrets.randbelow(1_000_000)`)
  - บันทึกรหัสลงฐานข้อมูลในรูปแบบ Password Hash เท่านั้น
  - กำหนดอายุ OTP 10 นาที จำกัดการลองผิดไม่เกิน 5 ครั้ง (`OTP_MAX_ATTEMPTS = 5`) และมี Cooldown 60 วินาที

### 6.3 OWASP Security Defenses
* **SQL Injection Defense:** ใช้ SQLAlchemy ORM ในการทำ Parameterized Queries ป้องกันคำสั่ง SQL แปลกปลอม 100%
* **Cross-Site Scripting (XSS) Defense:** ทำ Sanitization ข้อมูลนำเข้าและเข้ารหัส HTML Entities หน้าแสดงผล
* **Brute-Force & Rate Limiting:** จำกัดจำนวนคำขอเข้าสู่ระบบ (เช่น ตอบกลับ HTTP Status `429 Too Many Requests` เมื่อส่งคำขอเกินกำหนด)
* **Mass Assignment Defense:** ป้องกันไม่ให้ผู้ใช้ลงทะเบียนระบุค่า `role` เป็น Admin โดยบังคับกำหนดค่าเริ่มต้นเป็น `member` ใน Server Logic

---

## 7. ทฤษฎีการทดสอบระบบและประกันคุณภาพ (Software Testing & Quality Assurance)

### 7.1 Black Box Testing Methodology
ทดสอบการทำงานของระบบในมุมมองของผู้ใช้งานโดยพิจารณาเฉพาะข้อมูลนำเข้า (Inputs) และผลลัพธ์ที่ตอบกลับ (Outputs) โดยไม่ยึดติดกับโค้ดภายใน

### 7.2 Automated Test Execution & Environment Isolation
* **Test Isolation Pattern:** ใช้ฐานข้อมูล **SQLite In-Memory / Isolated Test DB** สำหรับการทดสอบอัตโนมัติ เพื่อป้องกันไม่ให้ข้อมูลจริงใน PostgreSQL เกิดความเสียหาย
* **Framework:** ใช้ `pytest` ร่วมกับ Flask Test Client เพื่อทดสอบแบบ End-to-End ผ่าน API
* **อัตราความสำเร็จ (Pass Rate):** ผ่านการทดสอบทั้งหมด **120 กรณีทดสอบ (100%)** ครอบคลุมฟังก์ชันหลัก, API, ความปลอดภัย และ UI Controls

---

## สรุปภาพรวมทฤษฎีในระบบ (Summary Table)

| หมวดหมู่ | ทฤษฎี / เทคโนโลยี | บทบาทหน้าที่ใน TradeSensei |
|---|---|---|
| **Time-Series ML** | Prophet (GAM Model) | พยากรณ์ราคาหุ้น 7 วันล่วงหน้า พร้อมย่อยสลาย Trend และ Seasonality |
| **Applied Math** | Logarithmic Transformation (`log1p`/`expm1`) | ปรับเสถียรภาพความผันผวนของราคาต่างสเกล และป้องกันราคาพยากรณ์ติดลบ |
| **Model Evaluation** | Hold-out Validation, MAE, MAPE | ประเมินความแม่นยำโมเดลบนชุดข้อมูลทดสอบ 14 วัน และแสดงค่า Accuracy % |
| **NLP** | TextBlob (Lexicon & Rule-based NLP) | วิเคราะห์อารมณ์ข่าวการเงิน (Polarity Score [-1, +1]) จัดกลุ่ม Pos/Neg/Neu |
| **Generative AI** | RAG Architecture + Gemini 1.5/2.0 Flash | ค้นคืนข้อมูล D2-D5 เพื่อตอบคำถามเรื่องหุ้นแบบมีข้อเท็จจริงอ้างอิง |
| **Financial Math** | Compound Interest & ROI Formula | จำลองการลงทุน Time Machine และเปรียบเทียบผลตอบแทนกับเงินฝากออมทรัพย์ |
| **Software Architecture** | DFD 1.0-5.0 & Router-Service-Model Pattern | จัดโครงสร้างการไหลของข้อมูลและแบ่งความรับผิดชอบของระบบ |
| **Cryptography** | scrypt KDF & Cryptographic OTP | แฮชรหัสผ่าน ป้องกัน Brute-force และสุ่มรหัสยืนยัน OTP รีเซ็ตรหัสผ่าน |
| **Cybersecurity** | JWT, RBAC, Parameterized Queries, Rate Limiter | ป้องกันช่องโหว่ OWASP Top 10 และควบคุมสิทธิ์ผู้ใช้ |
| **Quality Assurance** | Black Box Testing, Pytest Isolated Environment | ทดสอบอัตโนมัติ 120 Test Cases (ผ่าน 100%) |

---
*เอกสารนี้จัดทำขึ้นสำหรับโครงการ TradeSensei เพื่อสรุปกรอบทฤษฎีและเทคโนโลยีทั้งหมดที่ใช้ในระบบ*
