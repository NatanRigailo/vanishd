import logging
import os

from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(key_func=get_remote_address, default_limits=[])

log = logging.getLogger(__name__)


def create_app():
    app = Flask(__name__)
    # NOSONAR python:S4502 — CSRF N/A: JSON-only API, no session auth, no state-altering cookies.
    # Content-Type enforcement in create_secret() provides equivalent CORS-preflight protection.
    app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(32).hex()
    app.config["MAX_CONTENT_LENGTH"] = int(os.environ.get("MAX_CONTENT_LENGTH", 65536))

    _configure_logging()
    limiter.init_app(app)

    from app.db import init_db
    init_db()

    log.info(
        "startup max_ttl=%s rate_limit=%s cleanup_interval=%s",
        os.environ.get("MAX_TTL_SECONDS", 604800),
        os.environ.get("RATE_LIMIT_PER_MINUTE", 20),
        os.environ.get("CLEANUP_INTERVAL_SECONDS", 3600),
    )

    from app.cleanup import start_cleanup_thread
    start_cleanup_thread()

    from app.routes import bp
    app.register_blueprint(bp)

    app.after_request(_set_security_headers)

    return app


def _set_security_headers(response):
    csp = (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self'; "
        "font-src 'self'; "
        "img-src 'self'; "
        "connect-src 'self'; "
        "frame-ancestors 'none';"
    )
    response.headers["Content-Security-Policy"] = csp
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains"
    response.headers.pop("Server", None)
    return response


def _configure_logging():
    log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, log_level, logging.INFO)
    fmt = '{"time":"%(asctime)s","level":"%(levelname)s","msg":"%(message)s"}'
    logging.basicConfig(level=level, format=fmt)
