import logging
import os
import re
import time
import uuid

from flask import Blueprint, jsonify, render_template, request
from flask_limiter.errors import RateLimitExceeded

from app import limiter
from app.db import get_db

log = logging.getLogger(__name__)
bp = Blueprint("main", __name__)

MAX_TTL = int(os.environ.get("MAX_TTL_SECONDS", 604800))
RATE_LIMIT_POST = os.environ.get("RATE_LIMIT_POST_PER_MINUTE", "10")


def _sanitize(value):
    return re.sub(r"[\r\n\t\x00-\x1f\x7f]", "_", str(value))


@bp.app_errorhandler(RateLimitExceeded)
def handle_rate_limit(e):
    log.warning("rate_limit_exceeded ip=%s", _sanitize(request.remote_addr))
    return jsonify({"error": "too many requests"}), 429


@bp.app_errorhandler(413)
def handle_too_large(e):
    return jsonify({"error": "request too large"}), 413


@bp.route("/healthz", methods=["GET"])
def healthz():
    return jsonify({"status": "ok", "time": int(time.time())})


@bp.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@bp.route("/s/<secret_id>", methods=["GET"])
def view_secret(secret_id):
    return render_template("view.html", secret_id=secret_id)


@bp.route("/api/secrets", methods=["POST"])
@limiter.limit(f"{RATE_LIMIT_POST}/minute")
def create_secret():
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

    log.info("secret_created id=%s ttl=%d", secret_id, ttl)
    return jsonify({"id": secret_id}), 201


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
        log.warning(
            "secret_not_found id=%s ip=%s", _sanitize(secret_id), _sanitize(request.remote_addr)
        )
        return jsonify({"error": "secret not found or expired"}), 404

    log.info("secret_read id=%s ip=%s", _sanitize(secret_id), _sanitize(request.remote_addr))
    return jsonify({"ciphertext": row["ciphertext"], "iv": row["iv"], "salt": row["salt"]})
