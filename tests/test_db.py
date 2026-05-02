from unittest.mock import MagicMock, patch

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


def test_conn_pg_execute_converts_placeholders():
    mock_raw = MagicMock()
    mock_cur = MagicMock()
    mock_raw.cursor.return_value = mock_cur

    conn = db._Conn(mock_raw, is_pg=True)
    conn.execute("SELECT * WHERE id = ?", ("x",))

    mock_cur.execute.assert_called_once_with("SELECT * WHERE id = %s", ("x",))


def test_conn_pg_executescript_runs_statements():
    mock_raw = MagicMock()
    mock_cur = MagicMock()
    mock_raw.cursor.return_value = mock_cur

    conn = db._Conn(mock_raw, is_pg=True)
    conn.executescript("CREATE TABLE foo (id TEXT); CREATE INDEX idx ON foo(id);")

    assert mock_cur.execute.call_count == 2


def test_conn_pg_commit_and_close():
    mock_raw = MagicMock()
    conn = db._Conn(mock_raw, is_pg=True)
    conn.commit()
    conn.close()
    mock_raw.commit.assert_called_once()
    mock_raw.close.assert_called_once()


def test_get_db_postgres(monkeypatch):
    monkeypatch.setattr(db, "DATABASE_URL", "postgresql://u:p@host/dbname")
    mock_raw = MagicMock()
    with patch("psycopg2.connect", return_value=mock_raw):
        conn = db.get_db()
        assert isinstance(conn, db._Conn)
        conn.close()


def test_init_db_postgres(monkeypatch):
    monkeypatch.setattr(db, "DATABASE_URL", "postgresql://u:p@host/dbname")
    mock_raw = MagicMock()
    mock_cur = MagicMock()
    mock_raw.cursor.return_value = mock_cur
    with patch("psycopg2.connect", return_value=mock_raw):
        db.init_db()
    assert mock_cur.execute.called
