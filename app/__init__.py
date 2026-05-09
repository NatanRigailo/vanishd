import logging
import os
import time

from flask import Flask, g, request
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

    app.before_request(_start_timer)
    app.after_request(_record_request_duration)
    app.after_request(_set_security_headers)
    app.after_request(_set_lang_cookie)

    from app.i18n import get_locale, get_t

    @app.context_processor
    def inject_i18n():
        return {'t': get_t(), 'lang': get_locale()}

    return app


def _start_timer():
    g.start_time = time.time()


def _record_request_duration(response):
    if hasattr(g, "start_time") and request.endpoint != "main.metrics":
        from app.metrics import request_duration
        route = str(request.url_rule) if request.url_rule else "unknown"
        request_duration.labels(route=route, method=request.method).observe(
            time.time() - g.start_time
        )
    return response


def _set_lang_cookie(response):
    lang = request.args.get('lang')
    if lang in ('en', 'pt-BR'):
        response.set_cookie('lang', lang, max_age=60 * 60 * 24 * 365, samesite='Lax')
    return response


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
