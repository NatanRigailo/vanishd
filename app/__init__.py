import logging
import os

from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(key_func=get_remote_address, default_limits=[])

log = logging.getLogger(__name__)


def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(32).hex()

    _configure_logging()
    limiter.init_app(app)

    from app.db import init_db
    init_db()

    from app.cleanup import start_cleanup_thread
    start_cleanup_thread()

    from app.routes import bp
    app.register_blueprint(bp)

    return app


def _configure_logging():
    log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, log_level, logging.INFO)
    fmt = '{"time":"%(asctime)s","level":"%(levelname)s","msg":"%(message)s"}'
    logging.basicConfig(level=level, format=fmt)
