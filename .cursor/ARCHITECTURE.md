# TradeSensei — MVC Architecture & Scope Map

Aligned with [documents.md](./documents.md) (system specification) and [dictionary.md](./dictionary.md) (database).

---

## MVC mapping (Flask API + Vanilla frontend)

| Layer | Responsibility | Location |
|-------|----------------|----------|
| **Model** | DB schema, ORM entities (10 tables) | `backend/app/models/schema.py` |
| **View** | JSON HTTP responses (API contract for frontend) | `backend/app/routers/*.py` |
| **Controller** | Thin route handlers → delegate to services | `backend/app/routers/*.py` |
| **Service** | Business logic (Prophet, scrape, auth, RAG) | `backend/app/services/*.py` |
| **Core** | Config, DB extension, security helpers | `backend/app/core/` |

Frontend is **not** server-rendered MVC; it uses **page-based JS** (Presentation layer):

| UI role | Files |
|---------|--------|
| Pages (HTML) | `frontend/*.html` |
| Page controllers | `frontend/app.js`, `login.js`, `register.js`, `admin.js` |
| Shared utilities | `frontend/auth.js` |
| Styles | `frontend/style.css` |

---

## Project structure

```text
trade_sensei/
├── docker-compose.yml
├── .cursor/
│   ├── documents.md          # Scope & requirements (source of truth)
│   ├── dictionary.md         # DB field definitions
│   ├── claude.md             # AI coding rules
│   └── ARCHITECTURE.md       # This file
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── wsgi.py               # Flask entry (FLASK_APP=wsgi.py)
│   ├── scripts/
│   │   └── scraper.py        # Admin batch scrape CLI
│   └── app/                  # Application package
│       ├── __init__.py       # create_app() factory
│       ├── core/
│       │   ├── config.py
│       │   ├── database.py   # SQLAlchemy db instance
│       │   └── security.py   # JWT, passwords, seed admin
│       ├── models/
│       │   └── schema.py     # 10 tables (ER diagram)
│       ├── services/         # Business logic (MVC “Model” operations)
│       │   ├── auth_service.py
│       │   ├── stock_service.py
│       │   ├── predictor_service.py   # Prophet 7-day (§4.1)
│       │   ├── scraper_service.py     # yfinance pipeline (§4.1)
│       │   ├── admin_service.py
│       │   ├── copilot_service.py     # RAG + Gemini (§4.2) — Phase 2
│       │   └── backtest_service.py    # Time Machine (§2.2) — Phase 2
│       └── routers/            # HTTP controllers (MVC “Controller”)
│           ├── health.py
│           ├── auth.py         # Guest/Member login & register
│           ├── stocks.py       # Guest dashboard + OHLCV
│           ├── predictions.py  # Member on-demand Prophet
│           ├── news.py         # Guest news links
│           ├── admin.py        # Admin CRUD, scrape, train
│           ├── chatbot.py      # Member Copilot — Phase 2
│           └── backtest.py     # Member Time Machine — Phase 2
│
└── frontend/
    ├── index.html              # Guest + Member dashboard
    ├── login.html / login.js
    ├── register.html / register.js
    ├── admin.html / admin.js
    ├── auth.js                 # API base, nav, session
    └── style.css
```

---

## Scope → module map (from documents.md)

### §2.1 Guest
| Feature | Router | Service |
|---------|--------|---------|
| Dashboard / stock list | `stocks.py` | `stock_service` |
| Sector filter | — (frontend) | — |
| Plotly chart OHLCV | `stocks.py` `/stock-data/<symbol>` | `stock_service` |
| News links | `news.py` | `stock_service` |

### §2.2 Member
| Feature | Router | Service | Status |
|---------|--------|---------|--------|
| Register / Login | `auth.py` | `auth_service` | Done |
| AI prediction chart | `predictions.py` | `predictor_service` | Done |
| On-demand prediction | `predictions.py` | `predictor_service` | Done |
| Deep analysis | `analysis.py` | `analysis_service` + `sentiment_service` | Done |
| Time Machine backtest | `backtest.py` | `backtest_service` | Done |
| Sensei Copilot (RAG) | `chatbot.py` | `copilot_service` | Done (offline fallback without API key) |

### §2.3 Administrator
| Feature | Router | Service | Status |
|---------|--------|---------|--------|
| Master data CRUD | `admin.py` | `admin_service` | Done |
| Data scraper | `admin.py` `/run-scraper` | `scraper_service` | Done |
| Batch train Prophet | `admin.py` `/train-models` | `predictor_service` | Done |
| System logs | `admin.py` `/logs` | `admin_service` | Done |

### §4.1 Data pipeline
`Admin → scraper_service → historical_prices → predictor_service → price_predictions`

### §4.2 NLP & Copilot
`scraper → TextBlob → news_sentiments → copilot_service (strict D2–D5 grounding)`

Copilot only returns facts already stored in TradeSensei data stores. When a
`GEMINI_API_KEY` is configured, Gemini 2.5 Flash may rewrite those approved
facts into clearer Thai, but cannot receive extra sources or use conversation
history as factual context. Invalid model output falls back to deterministic
text; neither mode infers investment actions or uses world knowledge.

---

## DFD implementation traceability

The application follows the supplied DFD data stores as database tables: D1
`users`, D2 `stocks`, D3 `historical_prices`, D4 `news` + `news_sentiments`,
D5 `price_predictions` + `stock_models`, D6 `chat_history`, and D7
`system_logs`.

| DFD process | Implementation flow | Stored output |
|---|---|---|
| 2.1 Manage stock data | `admin.py` → `admin_service` | D2, D7 |
| 2.2 Fetch prices/news | `scraper_service.run_batch_scrape()` → yfinance → sentiment analysis | D3, D4, D7 |
| 3.1 Forecast prices | `predictor_service.run_prophet_forecast()` prepares D3 data, validates a hold-out window, predicts seven market days, and serializes metadata | D5, D7 |
| 3.2 Analyze news sentiment | `sentiment_service.analyze_stock_news()` | D4, D7 |
| 4.1–4.3 Dashboard/deep analysis/backtest | stock, analysis, prediction, and backtest routers | reads D2–D5 |
| 5.1–5.5 Copilot/RAG | `copilot_service` retrieves D3–D6 and records the exchange | D6, D7 |
| 6.1–6.2 Administration logs | `admin_service.get_system_logs()` | reads D7 |

Forecast quality metadata is held in D5's `stock_models.model_json`, including
the model configuration, training timestamp, validation window, MAE, and MAPE.
The frontend receives only this safe summary; raw model data remains internal.

---

## API routes (unchanged for frontend)

| Method | Path | Role |
|--------|------|------|
| GET | `/api/auth/config` | Public (Google client id) |
| POST | `/api/auth/login` | All |
| POST | `/api/auth/google` | Guest (Google ID token) |
| POST | `/api/auth/register` | Guest |
| POST | `/api/auth/forgot-password` | Guest (sends email OTP) |
| POST | `/api/auth/reset-password` | Guest (verifies OTP and changes password) |
| PUT | `/api/auth/change-password` | Member+ (JWT) |
| GET | `/api/stocks` | Guest |
| GET | `/api/stock-data/<symbol>` | Guest |
| GET | `/api/news/<symbol>` | Guest |
| GET | `/api/predict/<symbol>` | Member+ (JWT) |
| POST | `/api/admin/stocks` | Admin |
| DELETE | `/api/admin/stocks/<symbol>` | Admin |
| POST | `/api/admin/run-scraper` | Admin |
| GET | `/api/analysis/<symbol>` | Member+ (JWT) |
| POST | `/api/copilot/chat` | Member+ (JWT) |
| GET | `/api/copilot/history` | Member+ (JWT, own history only) |
| DELETE | `/api/copilot/history` | Member+ (JWT, clears own history) |
| POST | `/api/backtest/<symbol>` | Member+ (JWT) |
| GET | `/api/admin/logs` | Admin |
| POST | `/api/admin/train-models` | Admin (background) |

---

## Conventions

1. **Routers** — parse request, call one service method, return `jsonify`.
2. **Services** — no Flask imports; raise `ValueError` for business errors.
3. **Models** — SQLAlchemy only; no business logic.
4. **No features outside documents.md** without updating the spec first.
