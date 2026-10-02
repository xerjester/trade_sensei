FROM python:3.10-slim

# ตั้งค่า Working Directory ใน Container
WORKDIR /app

# ติดตั้ง System dependencies ที่จำเป็นสำหรับ Prophet และไลบรารีข้อมูล
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# คัดลอกไฟล์ requirements และติดตั้ง
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# คัดลอกโค้ดทั้งหมด
COPY . .

# สั่งรัน Flask ด้วย Gunicorn (รองรับ PORT ของ Render อัตโนมัติ)
ENV PORT=5000
EXPOSE 5000
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-5000} --workers 2 --timeout 120 wsgi:app"]