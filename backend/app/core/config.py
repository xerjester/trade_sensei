import os
from datetime import timedelta


class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'postgresql://postgres:password123@localhost:5432/tradesensei_db',
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECRET_KEY = os.environ.get('SECRET_KEY', '')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or os.environ.get('SECRET_KEY', '')

    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
    GEMINI_MODEL = os.environ.get('GEMINI_MODEL', 'gemini-2.5-flash').strip()
    DEPOSIT_RATE_ANNUAL = float(os.environ.get('DEPOSIT_RATE_ANNUAL', '0.025'))

    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '').strip()
    RESEND_API_KEY = os.environ.get('RESEND_API_KEY', '').strip()
    RESEND_FROM_EMAIL = os.environ.get(
        'RESEND_FROM_EMAIL', 'TradeSensei <onboarding@resend.dev>'
    ).strip()

    FLASK_DEBUG = os.environ.get('FLASK_DEBUG', '0') == '1'
    @staticmethod
    def _parse_cors_origins() -> tuple[str, ...]:
        origins = {
            'http://localhost:5500',
            'http://127.0.0.1:5500',
            'http://localhost:5501',
            'http://127.0.0.1:5501',
            'http://localhost:3000',
            'http://127.0.0.1:3000',
            'http://localhost:5000',
            'http://127.0.0.1:5000',
            'http://localhost:8080',
            'http://127.0.0.1:8080',
            'http://202.28.34.205:8080',
            'http://202.28.34.205',
            'https://202.28.34.205:8080',
            'https://202.28.34.205',
        }
        raw = os.environ.get('CORS_ORIGINS', '')
        for item in raw.split(','):
            clean = item.strip().strip('"\'').rstrip('/')
            if clean:
                origins.add(clean)
                if '://' in clean:
                    parts = clean.split('/')
                    if len(parts) >= 3:
                        origins.add(f'{parts[0]}//{parts[2]}')
        return tuple(origins)

    CORS_ORIGINS = _parse_cors_origins()
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', str(1024 * 1024)))
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        minutes=int(os.environ.get('JWT_ACCESS_TOKEN_MINUTES', '60'))
    )
    RATELIMIT_STORAGE_URI = os.environ.get('RATELIMIT_STORAGE_URI', 'memory://')

    @classmethod
    def validate(cls) -> None:
        """Fail closed when production secrets are absent or unsafe."""
        if cls.FLASK_DEBUG:
            if not cls.SECRET_KEY:
                cls.SECRET_KEY = 'dev-only-secret-change-me'
            if not cls.JWT_SECRET_KEY:
                cls.JWT_SECRET_KEY = cls.SECRET_KEY
            return

        weak_values = {'', 'change_me', 'dev-only-secret-change-me', 'trade-sensei-super-secret'}
        if cls.SECRET_KEY in weak_values or len(cls.SECRET_KEY) < 32:
            raise RuntimeError('SECRET_KEY ต้องเป็นค่าสุ่มอย่างน้อย 32 ตัวอักษรใน production')
        if cls.JWT_SECRET_KEY in weak_values or len(cls.JWT_SECRET_KEY) < 32:
            raise RuntimeError('JWT_SECRET_KEY ต้องเป็นค่าสุ่มอย่างน้อย 32 ตัวอักษรใน production')
