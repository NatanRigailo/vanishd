import os
import sqlite3

DATABASE_URL = os.environ.get("DATABASE_URL")
DATABASE_PATH = os.environ.get("DATABASE_PATH", "/data/vanishd.db")

_SCHEMA = """
CREATE TABLE IF NOT EXISTS secrets (
    id          TEXT    PRIMARY KEY,
    ciphertext  TEXT    NOT NULL,
    iv          TEXT    NOT NULL,
    salt        TEXT,
    created_at  INTEGER NOT NULL,
    expires_at  INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_secrets_expires_at ON secrets(expires_at);
"""


class _Conn:
    """Normalizes SQLite and PostgreSQL connection interfaces."""

    def __init__(self, raw, is_pg):
        self._raw = raw
        self._pg = is_pg

    def execute(self, sql, params=()):
        if self._pg:
            cur = self._raw.cursor()
            cur.execute(sql.replace("?", "%s"), params or ())
            return cur
        return self._raw.execute(sql, params)

    def executescript(self, sql):
        if self._pg:
            cur = self._raw.cursor()
            for stmt in (s.strip() for s in sql.split(";") if s.strip()):
                cur.execute(stmt)
        else:
            self._raw.executescript(sql)

    def commit(self):
        self._raw.commit()

    def close(self):
        self._raw.close()


def get_db():
    if DATABASE_URL:
        import psycopg2
        import psycopg2.extras
        raw = psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)
        return _Conn(raw, is_pg=True)

    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return _Conn(conn, is_pg=False)


def ping_db():
    conn = get_db()
    try:
        conn.execute("SELECT 1")
    finally:
        conn.close()


def init_db():
    if not DATABASE_URL:
        db_dir = os.path.dirname(DATABASE_PATH)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)

    conn = get_db()
    try:
        conn.executescript(_SCHEMA)
        conn.commit()
    finally:
        conn.close()
