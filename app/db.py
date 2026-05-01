import os
import sqlite3

DATABASE_PATH = os.environ.get("DATABASE_PATH", "/data/vanishd.db")


def get_db():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    db_dir = os.path.dirname(DATABASE_PATH)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

    conn = get_db()
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS secrets (
                id          TEXT    PRIMARY KEY,
                ciphertext  TEXT    NOT NULL,
                iv          TEXT    NOT NULL,
                salt        TEXT,
                created_at  INTEGER NOT NULL,
                expires_at  INTEGER NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_secrets_expires_at
                ON secrets(expires_at);
        """)
        conn.commit()
    finally:
        conn.close()
