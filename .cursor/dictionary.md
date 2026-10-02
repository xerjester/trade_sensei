# 📚 Data Dictionary (พจนานุกรมข้อมูล)
**Project:** Stock Prediction Platform
**Database:** PostgreSQL

เอกสารฉบับนี้อธิบายรายละเอียดของแต่ละคอลัมน์ (Field) ชนิดข้อมูล (Data Type) และความหมายในแต่ละตารางของฐานข้อมูล เพื่อใช้เป็นมาตรฐานในการพัฒนาและอ้างอิง

---

## 1. ตาราง `users` (ข้อมูลผู้ใช้งานและผู้ดูแลระบบ)
ใช้สำหรับจัดเก็บข้อมูลบัญชีผู้ใช้งาน สิทธิ์การเข้าถึง และรหัสผ่านที่เข้ารหัสแล้ว

| ชื่อคอลัมน์ (Field) | ประเภทข้อมูล (Type) | คีย์/ข้อจำกัด (Constraints) | คำอธิบาย (Description) |
| :--- | :--- | :--- | :--- |
| `user_id` | Integer | PK, Auto Increment | รหัสอ้างอิงผู้ใช้งาน (Primary Key) |
| `first_name` | String(50) | Not Null | ชื่อจริง |
| `last_name` | String(50) | - | นามสกุล |
| `email` | String(100) | Unique, Indexed, Not Null | อีเมลสำหรับใช้เข้าสู่ระบบ (ห้ามซ้ำ) |
| `password_hash` | String(255) | Not Null | รหัสผ่านที่ผ่านการเข้ารหัส (Bcrypt) |
| `role` | String(20) | Default='member' | สิทธิ์การใช้งาน ได้แก่ `member` หรือ `admin` |
| `created_at` | DateTime | Default=Current Timestamp | วันและเวลาที่สมัครสมาชิก |

---

## 2. ตาราง `stocks` (ข้อมูลหลักของสินทรัพย์/หุ้น)
ใช้สำหรับจัดเก็บข้อมูลพื้นฐานของหุ้น สินทรัพย์ หรือ Cryptocurrency ที่ระบบรองรับ

| ชื่อคอลัมน์ (Field) | ประเภทข้อมูล (Type) | คีย์/ข้อจำกัด (Constraints) | คำอธิบาย (Description) |
| :--- | :--- | :--- | :--- |
| `stock_id` | Integer | PK, Auto Increment | รหัสอ้างอิงหุ้น (Primary Key) |
| `symbol` | String(20) | Unique, Indexed, Not Null | สัญลักษณ์หุ้น (Ticker) เช่น `PTT.BK`, `AAPL`, `BTC-USD` |
| `company_name` | String(255) | - | ชื่อเต็มของบริษัท หรือ ชื่อสินทรัพย์ |
| `category` | String(50) | - | หมวดหมู่ธุรกิจ (Sector) หรือประเภทสินทรัพย์ |

---

## 3. ตาราง `user_favorites` (รายการหุ้นโปรดของสมาชิก)
ตารางความสัมพันธ์ (Mapping Table) สำหรับเก็บข้อมูลว่าผู้ใช้คนใด กดชื่นชอบหุ้นตัวไหนไว้บ้าง

| ชื่อคอลัมน์ (Field) | ประเภทข้อมูล (Type) | คีย์/ข้อจำกัด (Constraints) | คำอธิบาย (Description) |
| :--- | :--- | :--- | :--- |
| `favorite_id` | Integer | PK, Auto Increment | รหัสอ้างอิงรายการโปรด |
| `user_id` | Integer | FK -> users.user_id | รหัสอ้างอิงผู้ใช้งานที่กดชื่นชอบ |
| `stock_id` | Integer | FK -> stocks.stock_id | รหัสอ้างอิงหุ้นที่ถูกชื่นชอบ |
| `added_at` | DateTime | Default=Current Timestamp | วันและเวลาที่ผู้ใช้กดเพิ่มเข้ารายการโปรด |

---

## 4. ตาราง `historical_prices` (ข้อมูลราคาหุ้นย้อนหลัง)
ใช้สำหรับเก็บข้อมูลราคาเปิด ปิด สูง ต่ำ และปริมาณการซื้อขายรายวัน (EOD) สำหรับนำไปใช้เทรน AI

| ชื่อคอลัมน์ (Field) | ประเภทข้อมูล (Type) | คีย์/ข้อจำกัด (Constraints) | คำอธิบาย (Description) |
| :--- | :--- | :--- | :--- |
| `price_id` | Integer | PK, Auto Increment | รหัสอ้างอิงข้อมูลราคา |
| `stock_id` | Integer | FK -> stocks.stock_id | รหัสอ้างอิงหุ้น |
| `date` | DateTime | Indexed, Not Null | วันที่ของข้อมูลราคาการซื้อขาย |
| `open_price` | Float | - | ราคาเปิด (Open) |
| `high_price` | Float | - | ราคาสูงสุด (High) |
| `low_price` | Float | - | ราคาต่ำสุด (Low) |
| `close_price` | Float | - | ราคาปิด (Close) |
| `volume` | Float | - | ปริมาณการซื้อขาย (Volume) |

---

## 5. ตาราง `price_predictions` (ข้อมูลการทำนายราคา)
ใช้สำหรับเก็บผลลัพธ์ที่ได้จากการพยากรณ์ของโมเดล AI (Facebook Prophet) ล่วงหน้า 7 วัน

| ชื่อคอลัมน์ (Field) | ประเภทข้อมูล (Type) | คีย์/ข้อจำกัด (Constraints) | คำอธิบาย (Description) |
| :--- | :--- | :--- | :--- |
| `prediction_id` | Integer | PK, Auto Increment | รหัสอ้างอิงผลทำนาย |
| `stock_id` | Integer | FK -> stocks.stock_id | รหัสอ้างอิงหุ้นที่ถูกทำนาย |
| `predict_date`| DateTime | Indexed, Not Null | วันที่ในอนาคตที่โมเดลทำนายไว้ |
| `predicted_close`| Float | - | ราคาปิดที่ทำนาย (yhat) |
| `predicted_lower`| Float | - | ขอบเขตราคาต่ำสุดที่เป็นไปได้ (yhat_lower) |
| `predicted_upper`| Float | - | ขอบเขตราคาสูงสุดที่เป็นไปได้ (yhat_upper) |
| `trend_component`| Float | - | ค่าองค์ประกอบแนวโน้ม (Trend) เพื่อใช้วิเคราะห์ทิศทาง |
| `created_at` | DateTime | Default=Current Timestamp | วันและเวลาที่ประมวลผลคำทำนายชุดนี้ |

---

## 6. ตาราง `news` (ข้อมูลข่าวสาร)
ใช้สำหรับจัดเก็บข้อมูลข่าวสารทางการเงินที่เกี่ยวข้องกับหุ้นแต่ละตัว เพื่อนำไปวิเคราะห์อารมณ์ความรู้สึก

| ชื่อคอลัมน์ (Field) | ประเภทข้อมูล (Type) | คีย์/ข้อจำกัด (Constraints) | คำอธิบาย (Description) |
| :--- | :--- | :--- | :--- |
| `news_id` | Integer | PK, Auto Increment | รหัสอ้างอิงข่าว |
| `stock_id` | Integer | FK -> stocks.stock_id | รหัสอ้างอิงหุ้นที่ข่าวกล่าวถึง |
| `title` | String(255) | - | หัวข้อข่าว |
| `content` | Text | - | เนื้อหาข่าว (ฉบับย่อหรือเต็ม) |
| `url_link` | Text | - | ลิงก์ไปยังเว็บไซต์ต้นทางของข่าว |
| `published_date`| DateTime | - | วันและเวลาที่ข่าวถูกเผยแพร่ |

---

## 7. ตาราง `news_sentiments` (ผลวิเคราะห์อารมณ์ข่าว)
ใช้สำหรับจัดเก็บผลคะแนน NLP (Sentiment Analysis) ที่วิเคราะห์จากตาราง News

| ชื่อคอลัมน์ (Field) | ประเภทข้อมูล (Type) | คีย์/ข้อจำกัด (Constraints) | คำอธิบาย (Description) |
| :--- | :--- | :--- | :--- |
| `sentiment_id`| Integer | PK, Auto Increment | รหัสอ้างอิงผลวิเคราะห์ |
| `news_id` | Integer | FK -> news.news_id | รหัสอ้างอิงข่าวที่นำมาวิเคราะห์ |
| `sentiment_score`| Float | - | คะแนนอารมณ์จาก TextBlob (-1.0 แง่ลบ ถึง 1.0 แง่บวก) |
| `sentiment_label`| String(50) | - | ป้ายกำกับอารมณ์ (e.g., `Positive`, `Negative`, `Neutral`) |
| `reason_text` | Text | - | คำอธิบายหรือเหตุผลสนับสนุนผลการวิเคราะห์อารมณ์ |
| `analyzed_at` | DateTime | Default=Current Timestamp | วันและเวลาที่ทำการประมวลผลวิเคราะห์ |

---

## 8. ตาราง `system_logs` (บันทึกการทำงานของระบบ)
ใช้สำหรับติดตามและตรวจสอบ (Audit) การสั่งงานที่สำคัญของผู้ดูแลระบบ (Admin) เช่น การดึงข้อมูล หรือเทรนโมเดล

| ชื่อคอลัมน์ (Field) | ประเภทข้อมูล (Type) | คีย์/ข้อจำกัด (Constraints) | คำอธิบาย (Description) |
| :--- | :--- | :--- | :--- |
| `log_id` | Integer | PK, Auto Increment | รหัสอ้างอิง Log |
| `user_id` | Integer | FK -> users.user_id, Nullable | ไอดีผู้สั่งการ (หากเป็นงานอัตโนมัติจากระบบ จะเป็น Null) |
| `action_type` | String(100) | - | ประเภทการทำงาน เช่น `SCRAPE_DATA`, `TRAIN_MODEL` |
| `description` | Text | - | รายละเอียดผลการทำงาน เช่น จำนวนหุ้นที่ดึงสำเร็จ หรือข้อผิดพลาด |
| `created_at` | DateTime | Default=Current Timestamp | วันและเวลาที่เกิดเหตุการณ์ |

---

## 9. ตาราง `chat_history` (ประวัติการสนทนา AI Copilot)
ใช้สำหรับบันทึกการโต้ตอบระหว่างผู้ใช้งานและ AI ผู้ช่วยส่วนตัว

| ชื่อคอลัมน์ (Field) | ประเภทข้อมูล (Type) | คีย์/ข้อจำกัด (Constraints) | คำอธิบาย (Description) |
| :--- | :--- | :--- | :--- |
| `chat_id` | Integer | PK, Auto Increment | รหัสอ้างอิงข้อความสนทนา |
| `user_id` | Integer | FK -> users.user_id | รหัสอ้างอิงผู้ใช้งานที่ส่งคำถาม |
| `message` | Text | - | ข้อความคำถามหรือคำสั่งที่ผู้ใช้พิมพ์ |
| `provider` | String(50) | - | ชื่อผู้ประมวลผล (ในระบบนี้คือ `AI_Copilot`) |
| `response_text`| Text | - | ข้อความตอบกลับที่ AI ประมวลผลและสร้างขึ้น |
| `times` | DateTime | Default=Current Timestamp | วันและเวลาที่สนทนา |

---

## 10. ตาราง `stock_models` (พารามิเตอร์โมเดล AI)
ใช้สำหรับเก็บค่า Configuration และ Weights ของโมเดล Prophet ที่ผ่านการเทรนแล้ว เพื่อลดระยะเวลาการรันซ้ำ

| ชื่อคอลัมน์ (Field) | ประเภทข้อมูล (Type) | คีย์/ข้อจำกัด (Constraints) | คำอธิบาย (Description) |
| :--- | :--- | :--- | :--- |
| `stockmodel_id`| Integer | PK, Auto Increment | รหัสอ้างอิงพารามิเตอร์โมเดล |
| `stock_id` | Integer | FK -> stocks.stock_id | รหัสอ้างอิงหุ้นที่เป็นเจ้าของโมเดลนี้ |
| `model_json` | Text | - | ข้อมูลพารามิเตอร์ของโมเดลที่บันทึกในรูปแบบ JSON String |
| `updated_at` | DateTime | Default=Current Timestamp | วันและเวลาที่เทรนโมเดลตัวนี้สำเร็จล่าสุด |