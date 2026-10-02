from flask import Flask, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from app.core.config import Config
from app.core.database import db
from app.core.db_migrate import apply_user_auth_columns
from app.core.limiter import limiter
from app.core.security import seed_default_users
from app.routers import register_blueprints
from app.services.scheduler_service import start_scheduler


def create_app():
    Config.validate()

    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['SECRET_KEY'] = Config.SECRET_KEY
    app.config['JWT_SECRET_KEY'] = Config.JWT_SECRET_KEY
    app.config['JSON_SORT_KEYS'] = False

    CORS(
        app,
        resources={r'/api/*': {
            'origins': Config.CORS_ORIGINS,
            'methods': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
            'allow_headers': ['Content-Type', 'Authorization'],
        }},
        supports_credentials=False,
        max_age=600,
    )

    @app.before_request
    def require_json_for_api_writes():
        """Reject ambiguous write payloads before they reach route logic."""
        if (
            request.path.startswith('/api/')
            and request.method in {'POST', 'PUT', 'PATCH'}
            and (request.content_length or 0) > 0
            and not request.is_json
        ):
            return {'status': 'error', 'message': 'คำขอต้องอยู่ในรูปแบบ application/json'}, 415

    @app.errorhandler(404)
    def not_found(_error):
        return {'status': 'error', 'message': 'ไม่พบหน้าหรือข้อมูลที่ร้องขอ'}, 404

    @app.errorhandler(500)
    def internal_error(_error):
        db.session.rollback()
        return {'status': 'error', 'message': 'เกิดข้อผิดพลาดภายในระบบ กรุณาลองใหม่อีกครั้ง'}, 500

    @app.errorhandler(413)
    def payload_too_large(_error):
        return {'status': 'error', 'message': 'ข้อมูลที่ส่งมีขนาดใหญ่เกินกำหนด'}, 413

    @app.errorhandler(429)
    def rate_limited(_error):
        return {'status': 'error', 'message': 'ส่งคำขอมากเกินไป กรุณาลองใหม่ภายหลัง'}, 429

    @app.after_request
    def set_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'
        response.headers['Cross-Origin-Resource-Policy'] = 'same-site'
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; object-src 'none'; base-uri 'self'; "
            "frame-ancestors 'none'; form-action 'self'"
        )
        if request.path.startswith('/api/auth/'):
            response.headers['Cache-Control'] = 'no-store, max-age=0'
            response.headers['Pragma'] = 'no-cache'
        if not app.debug:
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        return response

    db.init_app(app)
    jwt = JWTManager(app)
    limiter.init_app(app)

    @jwt.unauthorized_loader
    def missing_jwt(_reason):
        return {'status': 'error', 'message': 'กรุณาเข้าสู่ระบบ'}, 401

    @jwt.invalid_token_loader
    def invalid_jwt(_reason):
        return {'status': 'error', 'message': 'โทเค็นไม่ถูกต้องหรือหมดอายุ'}, 401

    register_blueprints(app)

    with app.app_context():
        db.create_all()
        apply_user_auth_columns()
        seed_default_users()

    start_scheduler(app)

    return app
