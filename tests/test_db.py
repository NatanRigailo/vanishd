import app.db as db


def test_init_db_creates_table(app):
    conn = db.get_db()
    try:
        row = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='secrets'"
        ).fetchone()
        assert row is not None
    finally:
        conn.close()


def test_get_db_returns_connection(app):
    conn = db.get_db()
    try:
        assert conn.execute("SELECT 1").fetchone()[0] == 1
    finally:
        conn.close()


def test_ping_db(app):
    db.ping_db()
