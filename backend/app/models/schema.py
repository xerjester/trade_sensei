from datetime import datetime

from sqlalchemy.dialects.postgresql import JSONB

from app.core.database import db


class Stock(db.Model):
    __tablename__ = 'stocks'
    stock_id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), unique=True, nullable=False, index=True)
    company_name = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    historical_prices = db.relationship(
        'HistoricalPrice', backref='stock', lazy=True, cascade='all, delete-orphan'
    )
    news = db.relationship('News', backref='stock', lazy=True, cascade='all, delete-orphan')
    predictions = db.relationship(
        'PricePrediction', backref='stock', lazy=True, cascade='all, delete-orphan'
    )
    models = db.relationship(
        'StockModel', backref='stock', lazy=True, cascade='all, delete-orphan'
    )


class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.Text, nullable=True)
    google_id = db.Column(db.String(128), unique=True, nullable=True, index=True)
    role = db.Column(db.String(20), default='member')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    favorites = db.relationship(
        'UserFavorite', backref='user', lazy=True, cascade='all, delete-orphan'
    )
    chats = db.relationship(
        'ChatHistory', backref='user', lazy=True, cascade='all, delete-orphan'
    )
    logs = db.relationship('SystemLog', backref='user', lazy=True)


class HistoricalPrice(db.Model):
    __tablename__ = 'historical_prices'
    price_id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.Integer, db.ForeignKey('stocks.stock_id', ondelete='CASCADE'))
    date = db.Column(db.Date, nullable=False, index=True)
    open_price = db.Column(db.Numeric(15, 4))
    high_price = db.Column(db.Numeric(15, 4))
    low_price = db.Column(db.Numeric(15, 4))
    close_price = db.Column(db.Numeric(15, 4))
    volume = db.Column(db.BigInteger)

    __table_args__ = (db.UniqueConstraint('stock_id', 'date', name='uq_stock_date'),)


class News(db.Model):
    __tablename__ = 'news'
    news_id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.Integer, db.ForeignKey('stocks.stock_id', ondelete='CASCADE'), index=True)
    title = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text)
    url_link = db.Column(db.Text)
    published_date = db.Column(db.DateTime)

    sentiments = db.relationship(
        'NewsSentiment', backref='news_article', lazy=True, cascade='all, delete-orphan'
    )


class NewsSentiment(db.Model):
    __tablename__ = 'news_sentiments'
    sentiment_id = db.Column(db.Integer, primary_key=True)
    news_id = db.Column(db.Integer, db.ForeignKey('news.news_id', ondelete='CASCADE'))
    sentiment_score = db.Column(db.Numeric(5, 4))
    sentiment_label = db.Column(db.String(20))
    reason_text = db.Column(db.Text)
    analyzed_at = db.Column(db.DateTime, default=datetime.utcnow)


class PricePrediction(db.Model):
    __tablename__ = 'price_predictions'
    prediction_id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.Integer, db.ForeignKey('stocks.stock_id', ondelete='CASCADE'))
    predict_date = db.Column(db.Date, nullable=False, index=True)
    predicted_open = db.Column(db.Numeric(15, 4))
    predicted_high = db.Column(db.Numeric(15, 4))
    predicted_low = db.Column(db.Numeric(15, 4))
    predicted_close = db.Column(db.Numeric(15, 4))
    predicted_volume = db.Column(db.BigInteger)
    trend_component = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class StockModel(db.Model):
    __tablename__ = 'stock_models'
    stockmodel_id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.Integer, db.ForeignKey('stocks.stock_id', ondelete='CASCADE'))
    model_json = db.Column(JSONB)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class UserFavorite(db.Model):
    __tablename__ = 'user_favorites'
    favorite_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'))
    stock_id = db.Column(db.Integer, db.ForeignKey('stocks.stock_id', ondelete='CASCADE'))
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('user_id', 'stock_id', name='uq_user_stock'),)


class ChatHistory(db.Model):
    __tablename__ = 'chat_history'
    chat_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'))
    message = db.Column(db.Text, nullable=False)
    response_text = db.Column(db.Text)
    provider = db.Column(db.String(50))
    times = db.Column(db.DateTime, default=datetime.utcnow)


class PasswordResetOtp(db.Model):
    """Short-lived, single-use OTPs for the public forgot-password flow."""
    __tablename__ = 'password_reset_otps'
    reset_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    code_hash = db.Column(db.String(255), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False, index=True)
    attempts = db.Column(db.Integer, default=0, nullable=False)
    used_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class SystemLog(db.Model):
    __tablename__ = 'system_logs'
    log_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='SET NULL'))
    action_type = db.Column(db.String(100))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
