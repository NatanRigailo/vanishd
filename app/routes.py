import time

from flask import Blueprint, jsonify

bp = Blueprint("main", __name__)


@bp.route("/healthz")
def healthz():
    return jsonify({"status": "ok", "time": int(time.time())})
