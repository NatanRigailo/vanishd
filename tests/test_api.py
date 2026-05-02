import time
from unittest.mock import patch

import app.db as db


def test_healthz(client):
    r = client.get("/healthz")
    assert r.status_code == 200
    data = r.get_json()
    assert data["status"] == "ok"
    assert data["db"] == "ok"


def test_create_secret_valid(client):
    r = client.post("/api/secrets", json={"ciphertext": "abc", "iv": "iv", "ttl": 3600})
    assert r.status_code == 201
    assert "id" in r.get_json()


def test_create_secret_missing_ciphertext(client):
    r = client.post("/api/secrets", json={"iv": "iv", "ttl": 3600})
    assert r.status_code == 400


def test_create_secret_missing_iv(client):
    r = client.post("/api/secrets", json={"ciphertext": "abc", "ttl": 3600})
    assert r.status_code == 400


def test_create_secret_ttl_zero(client):
    r = client.post("/api/secrets", json={"ciphertext": "abc", "iv": "iv", "ttl": 0})
    assert r.status_code == 400


def test_create_secret_ttl_too_large(client):
    r = client.post("/api/secrets", json={"ciphertext": "abc", "iv": "iv", "ttl": 9999999})
    assert r.status_code == 400


def test_create_secret_invalid_ttl(client):
    r = client.post("/api/secrets", json={"ciphertext": "abc", "iv": "iv", "ttl": "nan"})
    assert r.status_code == 400


def test_read_secret_success(client):
    secret_id = client.post(
        "/api/secrets", json={"ciphertext": "hello", "iv": "iv", "ttl": 3600}
    ).get_json()["id"]

    r = client.get(f"/api/secrets/{secret_id}")
    assert r.status_code == 200
    data = r.get_json()
    assert data["ciphertext"] == "hello"
    assert data["iv"] == "iv"


def test_read_secret_one_time(client):
    secret_id = client.post(
        "/api/secrets", json={"ciphertext": "once", "iv": "iv", "ttl": 3600}
    ).get_json()["id"]

    assert client.get(f"/api/secrets/{secret_id}").status_code == 200
    assert client.get(f"/api/secrets/{secret_id}").status_code == 404


def test_read_secret_not_found(client):
    assert client.get("/api/secrets/does-not-exist").status_code == 404


def test_read_secret_expired(client):
    now = int(time.time())
    conn = db.get_db()
    conn.execute(
        "INSERT INTO secrets (id, ciphertext, iv, salt, created_at, expires_at) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        ("expired-id", "ct", "iv", None, now - 100, now - 1),
    )
    conn.commit()
    conn.close()

    assert client.get("/api/secrets/expired-id").status_code == 404


def test_healthz_db_error(client):
    with patch("app.routes.ping_db", side_effect=RuntimeError("db down")):
        r = client.get("/healthz")
    assert r.status_code == 503
    assert r.get_json()["db"] == "error"


def test_index_page(client):
    assert client.get("/").status_code == 200


def test_view_page(client):
    assert client.get("/s/some-id").status_code == 200


def test_404_page_returns_html(client):
    r = client.get("/this-route-does-not-exist")
    assert r.status_code == 404
    assert b"404" in r.data


def test_404_api_returns_json(client):
    r = client.get("/api/nonexistent")
    assert r.status_code == 404
    assert r.get_json()["error"] == "not found"


def test_413_api_returns_json(app):
    app.config["MAX_CONTENT_LENGTH"] = 50
    r = app.test_client().post(
        "/api/secrets",
        data=b"x" * 100,
        content_type="application/json",
    )
    assert r.status_code == 413
    assert r.get_json()["error"] == "request too large"


def test_413_page_returns_html(app):
    app.config["MAX_CONTENT_LENGTH"] = 50
    with patch("app.routes._wants_json", return_value=False):
        r = app.test_client().post(
            "/api/secrets",
            data=b"x" * 100,
            content_type="application/json",
        )
    assert r.status_code == 413
    assert b"413" in r.data


def test_500_api_returns_json(app):
    app.config["PROPAGATE_EXCEPTIONS"] = False
    with patch("app.routes.get_db", side_effect=RuntimeError("db")):
        r = app.test_client().get("/api/secrets/x")
    assert r.status_code == 500
    assert r.get_json()["error"] == "internal server error"


def test_500_page_returns_html(app):
    app.config["PROPAGATE_EXCEPTIONS"] = False
    with patch("app.routes._wants_json", return_value=False):
        with patch("app.routes.get_db", side_effect=RuntimeError("db")):
            r = app.test_client().get("/api/secrets/x")
    assert r.status_code == 500
    assert b"500" in r.data


def test_rate_limit_returns_429(tmp_path, monkeypatch):
    import app.db as _db_module
    monkeypatch.setattr(_db_module, "DATABASE_PATH", str(tmp_path / "rl.db"))
    from app import create_app
    application = create_app()
    application.config["PROPAGATE_EXCEPTIONS"] = False
    client = application.test_client()
    for _ in range(10):
        client.post("/api/secrets", json={"ciphertext": "x", "iv": "iv", "ttl": 3600})
    r = client.post("/api/secrets", json={"ciphertext": "x", "iv": "iv", "ttl": 3600})
    assert r.status_code == 429
    assert r.get_json()["error"] == "too many requests"
