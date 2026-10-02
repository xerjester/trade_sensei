"""Rate limiting for public and expensive API endpoints."""
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


# A shared limiter instance is initialised by the Flask app factory. Production
# deployments should set RATELIMIT_STORAGE_URI to Redis so limits survive restarts.
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=['3600 per hour', '120 per minute'],
)
