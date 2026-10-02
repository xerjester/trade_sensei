from app.routers.admin import admin_bp
from app.routers.analysis import analysis_bp
from app.routers.auth import auth_bp
from app.routers.backtest import backtest_bp
from app.routers.chatbot import chatbot_bp
from app.routers.health import health_bp
from app.routers.news import news_bp
from app.routers.predictions import predictions_bp
from app.routers.stocks import stocks_bp


def register_blueprints(app):
    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(stocks_bp)
    app.register_blueprint(predictions_bp)
    app.register_blueprint(news_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(chatbot_bp)
    app.register_blueprint(backtest_bp)
