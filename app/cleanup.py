import logging
import os
import threading
import time

from app.db import get_db

log = logging.getLogger(__name__)

CLEANUP_INTERVAL = int(os.environ.get("CLEANUP_INTERVAL_SECONDS", 3600))


def cleanup_once():
    conn = get_db()
    try:
        result = conn.execute(
            "DELETE FROM secrets WHERE expires_at <= ?", (int(time.time()),)
        )
        conn.commit()
        if result.rowcount:
            log.info("cleanup_expired count=%d", result.rowcount)
    finally:
        conn.close()


def _run():
    while True:
        time.sleep(CLEANUP_INTERVAL)
        try:
            cleanup_once()
        except Exception:
            log.exception("cleanup_error")


def start_cleanup_thread():
    t = threading.Thread(target=_run, name="cleanup", daemon=True)
    t.start()
    log.info("cleanup_thread_started interval_seconds=%d", CLEANUP_INTERVAL)
