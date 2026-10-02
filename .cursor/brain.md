# 🤖 AI Assistant Vibe & Context Rules
**Project Name:** Stock Prediction Platform (TradeSensei)
**Role:** Expert Full-Stack Developer — Python Flask (MVC) + Vanilla JavaScript.

**Scope:** Read [documents.md](./documents.md) before adding features. Architecture: [ARCHITECTURE.md](./ARCHITECTURE.md).

## 🎯 Coding Philosophy
- **Lightweight frontend:** Vanilla HTML/CSS/JS + Plotly.js only. No React/Vue/Tailwind unless asked.
- **MVC backend:** Routers (controllers) → Services (logic) → Models (schema). Keep routers thin.
- **Graceful errors:** User-friendly JSON messages; never leak stack traces to clients.
- **Responsive UI:** Flexbox/Grid, mobile nav hamburger.

## 🛠 Tech Stack
- **Frontend:** HTML5, `style.css`, page JS, Plotly.js (CDN)
- **Backend:** Python 3.10, Flask, Flask-JWT-Extended, Blueprints
- **Database:** PostgreSQL 15, SQLAlchemy 2.0
- **AI:** Prophet, TextBlob, Gemini (Copilot — planned)
- **Data:** yfinance, Pandas
- **DevOps:** Docker Compose

## 📂 Project Structure (MVC)

```text
trade_sensei/
├── docker-compose.yml
├── backend/
│   ├── wsgi.py                 # FLASK_APP entry
│   ├── requirements.txt
│   ├── scripts/scraper.py
│   └── app/
│       ├── __init__.py         # create_app()
│       ├── core/               # config, database, security
│       ├── models/schema.py    # 10 tables
│       ├── services/           # business logic
│       └── routers/            # Flask Blueprints (controllers)
└── frontend/
    ├── index.html              # Dashboard (Guest + Member)
    ├── login.html / register.html / admin.html
    ├── auth.js                 # shared API + nav
    └── *.js per page
```

## Er-Diagram
erDiagram
    USERS ||--o{ USER_FAVORITES : "manages"
    USERS ||--o{ CHAT_HISTORY : "queries"
    USERS ||--o{ SYSTEM_LOGS : "executes"
    STOCKS ||--o{ USER_FAVORITES : "monitored_by"
    STOCKS ||--o{ HISTORICAL_PRICES : "logs_ohlcv"
    STOCKS ||--o{ PRICE_PREDICTIONS : "projects"
    STOCKS ||--o{ NEWS : "tags"
    STOCKS ||--o{ STOCK_MODELS : "configures"
    NEWS ||--|| NEWS_SENTIMENTS : "scores"
