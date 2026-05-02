import time

import app.db as db


def test_cleanup_deletes_expired_and_keeps_active(app):
    now = int(time.time())
    conn = db.get_db()
    conn.execute(
        "INSERT INTO secrets (id, ciphertext, iv, salt, created_at, expires_at) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        ("expired", "ct", "iv", None, now - 200, now - 1),
    )
    conn.execute(
        "INSERT INTO secrets (id, ciphertext, iv, salt, created_at, expires_at) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        ("active", "ct", "iv", None, now, now + 3600),
    )
    conn.commit()
    conn.close()

    conn = db.get_db()
    conn.execute("DELETE FROM secrets WHERE expires_at <= ?", (int(time.time()),))
    conn.commit()
    ids = [r[0] for r in conn.execute("SELECT id FROM secrets").fetchall()]
    conn.close()

    assert "expired" not in ids
    assert "active" in ids
