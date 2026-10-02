# Security notes — TradeSensei

## Environment variables (required for production)

| Variable | Purpose |
|----------|---------|
| `SECRET_KEY` | Flask session signing — use a long random string |
| `JWT_SECRET_KEY` | JWT signing — use a different long random string |
| `GOOGLE_CLIENT_ID` | Google OAuth Web client ID (public in frontend) |
| `GEMINI_API_KEY` | Server-side only — never commit to git |

Copy `.env.example` to `.env` and fill in values before deploying.

## Authentication

- Passwords hashed with Werkzeug (scrypt).
- API uses JWT (`Authorization: Bearer <token>`).
- Google Sign-In: frontend sends ID token; backend verifies with Google (`google-auth`).
- Admin routes require `admin` role in JWT.

## Google OAuth setup

1. [Google Cloud Console](https://console.cloud.google.com/apis/credentials) → Create **OAuth 2.0 Client ID** → **Web application**.
2. **Authorized JavaScript origins** (examples):
   - `http://localhost:5500`
   - `http://127.0.0.1:5500`
   - Your production frontend URL
3. Set `GOOGLE_CLIENT_ID` in `.env` and restart backend.

## Hardening checklist

- [ ] Strong `SECRET_KEY` / `JWT_SECRET_KEY` in production
- [ ] `FLASK_DEBUG=0` in production
- [ ] HTTPS in production (required for secure cookies if added later)
- [ ] Restrict CORS origins in `app/__init__.py` if exposing API publicly
- [ ] Rotate `GEMINI_API_KEY` if ever exposed
