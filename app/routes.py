import logging
import os
import re
import time
import uuid

from flask import Blueprint, jsonify, render_template, request
from flask_limiter.errors import RateLimitExceeded
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app import limiter
from app.db import get_db, ping_db
from app.i18n import get_t
from app.metrics import secrets_created, secrets_not_found, secrets_read

log = logging.getLogger(__name__)
bp = Blueprint("main", __name__)

MAX_TTL = int(os.environ.get("MAX_TTL_SECONDS", 604800))
RATE_LIMIT_POST = os.environ.get("RATE_LIMIT_POST_PER_MINUTE", "10")


def _sanitize(value):
    return re.sub(r"[\r\n\t\x00-\x1f\x7f]", "_", str(value))


def _wants_json():
    return request.path.startswith("/api/")


def _error_page(code, message):
    return render_template("error.html", code=code, message=message), code


@bp.app_errorhandler(RateLimitExceeded)
def handle_rate_limit(e):
    log.warning("rate_limit_exceeded ip=%s", _sanitize(request.remote_addr))
    return jsonify({"error": "too many requests"}), 429


@bp.app_errorhandler(413)
def handle_too_large(e):
    if _wants_json():
        return jsonify({"error": "request too large"}), 413
    return _error_page(413, get_t()["err_too_large"])


@bp.app_errorhandler(404)
def handle_not_found(e):
    if _wants_json():
        return jsonify({"error": "not found"}), 404
    return _error_page(404, get_t()["err_not_found"])


@bp.app_errorhandler(500)
def handle_server_error(e):
    log.exception("internal_server_error")
    if _wants_json():
        return jsonify({"error": "internal server error"}), 500
    return _error_page(500, get_t()["err_server"])


@bp.route("/metrics", methods=["GET"])
def metrics():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}


@bp.route("/healthz", methods=["GET"])
def healthz():
    try:
        ping_db()
        db_status = "ok"
    except Exception:
        log.exception("healthz_db_error")
        db_status = "error"

    status = "ok" if db_status == "ok" else "error"
    code = 200 if status == "ok" else 503
    return jsonify({"status": status, "db": db_status, "time": int(time.time())}), code


@bp.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@bp.route("/s/<secret_id>", methods=["GET"])
def view_secret(secret_id):
    return render_template("view.html", secret_id=secret_id)


@bp.route("/api/secrets", methods=["POST"])
@limiter.limit(f"{RATE_LIMIT_POST}/minute")
def create_secret():
    if not request.is_json:
        return jsonify({"error": "content-type must be application/json"}), 415
    data = request.get_json(silent=True) or {}
    ciphertext = (data.get("ciphertext") or "").strip()
    iv = (data.get("iv") or "").strip()
    salt = (data.get("salt") or "").strip() or None

    try:
        ttl = int(data.get("ttl", 86400))
    except (ValueError, TypeError):
        return jsonify({"error": "ttl must be an integer"}), 400

    if not ciphertext or not iv:
        return jsonify({"error": "ciphertext and iv are required"}), 400
    if not (1 <= ttl <= MAX_TTL):
        return jsonify({"error": f"ttl must be between 1 and {MAX_TTL}"}), 400

    secret_id = str(uuid.uuid4())
    now = int(time.time())

    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO secrets (id, ciphertext, iv, salt, created_at, expires_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (secret_id, ciphertext, iv, salt, now, now + ttl),
        )
        conn.commit()
    finally:
        conn.close()

    secrets_created.inc()
    log.info("secret_created id=%s ttl=%d", secret_id, ttl)
    return jsonify({"id": secret_id}), 201


@bp.route("/api/secrets/<secret_id>", methods=["HEAD"])
@limiter.limit(f"{os.environ.get('RATE_LIMIT_PER_MINUTE', '20')}/minute")
def check_secret(secret_id):
    conn = get_db()
    try:
        row = conn.execute(
            "SELECT 1 FROM secrets WHERE id = ? AND expires_at > ?",
            (secret_id, int(time.time())),
        ).fetchone()
    finally:
        conn.close()
    return "", 200 if row else 404


@bp.route("/api/secrets/<secret_id>", methods=["GET"])
@limiter.limit(f"{os.environ.get('RATE_LIMIT_PER_MINUTE', '20')}/minute")
def read_secret(secret_id):
    conn = get_db()
    try:
        row = conn.execute(
            "DELETE FROM secrets WHERE id = ? AND expires_at > ? "
            "RETURNING ciphertext, iv, salt",
            (secret_id, int(time.time())),
        ).fetchone()
        conn.commit()
    finally:
        conn.close()

    if row is None:
        secrets_not_found.inc()
        log.warning(
            "secret_not_found id=%s ip=%s", _sanitize(secret_id), _sanitize(request.remote_addr)
        )
        return jsonify({"error": "secret not found or expired"}), 404

    secrets_read.inc()
    log.info("secret_read id=%s ip=%s", _sanitize(secret_id), _sanitize(request.remote_addr))
    return jsonify({"ciphertext": row["ciphertext"], "iv": row["iv"], "salt": row["salt"]})
