"""TextBlob sentiment analysis for news (documents.md §4.2)."""
from textblob import TextBlob

from app.core.database import db
from app.models import News, NewsSentiment, SystemLog


def _label_from_polarity(polarity: float) -> str:
    if polarity > 0.1:
        return 'Positive'
    if polarity < -0.1:
        return 'Negative'
    return 'Neutral'


def analyze_news_item(news: News) -> NewsSentiment:
    text = news.title or ''
    if news.content:
        text = f'{text} {news.content}'
    blob = TextBlob(text)
    polarity = round(blob.sentiment.polarity, 4)
    label = _label_from_polarity(polarity)
    reason = (
        f'TextBlob polarity {polarity:+.2f} — '
        f'{"แง่บวก" if label == "Positive" else "แง่ลบ" if label == "Negative" else "เป็นกลาง"}'
    )
    existing = NewsSentiment.query.filter_by(news_id=news.news_id).first()
    if existing:
        existing.sentiment_score = polarity
        existing.sentiment_label = label
        existing.reason_text = reason
        return existing

    row = NewsSentiment(
        news_id=news.news_id,
        sentiment_score=polarity,
        sentiment_label=label,
        reason_text=reason,
    )
    db.session.add(row)
    return row


def analyze_stock_news(stock_id: int) -> int:
    """DFD 3.2: analyze unscored D4 news, persist results, and create a D7 audit log."""
    news_items = News.query.filter_by(stock_id=stock_id).all()
    count = 0
    for news in news_items:
        if NewsSentiment.query.filter_by(news_id=news.news_id).first():
            continue
        analyze_news_item(news)
        count += 1
    if count:
        # The log makes the NLP pipeline observable from the admin log screen.
        db.session.add(SystemLog(
            action_type='ANALYZE_NEWS_SENTIMENT',
            description=f'วิเคราะห์อารมณ์ข่าว stock_id={stock_id} จำนวน {count} เรื่อง',
        ))
        db.session.commit()
    return count


def get_sentiment_summary(stock_id: int) -> dict:
    """Aggregate sentiment for deep analysis and RAG."""
    analyze_stock_news(stock_id)

    rows = (
        db.session.query(NewsSentiment, News)
        .join(News, NewsSentiment.news_id == News.news_id)
        .filter(News.stock_id == stock_id)
        .order_by(News.published_date.desc())
        .limit(10)
        .all()
    )

    if not rows:
        return {
            'average_score': 0.0,
            'overall_label': 'Neutral',
            'positive_count': 0,
            'negative_count': 0,
            'neutral_count': 0,
            'items': [],
        }

    scores = [float(s.sentiment_score) for s, _ in rows]
    avg = sum(scores) / len(scores)
    items = []
    pos = neg = neu = 0
    for sent, news in rows:
        if sent.sentiment_label == 'Positive':
            pos += 1
        elif sent.sentiment_label == 'Negative':
            neg += 1
        else:
            neu += 1
        items.append({
            'title': news.title,
            'score': float(sent.sentiment_score),
            'label': sent.sentiment_label,
            'reason': sent.reason_text,
        })

    return {
        'average_score': round(avg, 4),
        'overall_label': _label_from_polarity(avg),
        'positive_count': pos,
        'negative_count': neg,
        'neutral_count': neu,
        'items': items,
    }
