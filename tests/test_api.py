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


def test_handle_too_large(app):
    app.config["MAX_CONTENT_LENGTH"] = 50
    r = app.test_client().post(
        "/api/secrets",
        data=b"x" * 100,
        content_type="application/json",
    )
    assert r.status_code == 413


def test_index_page(client):
    assert client.get("/").status_code == 200


def test_view_page(client):
    assert client.get("/s/some-id").status_code == 200
