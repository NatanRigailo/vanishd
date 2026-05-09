import time

import pytest
from prometheus_client import REGISTRY

import app.db as _db_module


@pytest.fixture()
def app(tmp_path, monkeypatch):
    monkeypatch.setattr(_db_module, "DATABASE_PATH", str(tmp_path / "test.db"))
    from app import create_app
    application = create_app()
    application.config["TESTING"] = True
    application.config["RATELIMIT_ENABLED"] = False
    yield application


@pytest.fixture()
def client(app):
    return app.test_client()


def _val(name, labels=None):
    v = REGISTRY.get_sample_value(name, labels or {})
    return v or 0.0


def _post_secret(client, ttl=60):
    return client.post(
        "/api/secrets",
        json={"ciphertext": "abc", "iv": "def", "ttl": ttl},
        content_type="application/json",
    )


def test_create_increments_counter(client):
    before = _val("vanishd_secrets_created_total")
    resp = _post_secret(client)
    assert resp.status_code == 201
    assert _val("vanishd_secrets_created_total") - before == 1.0


def test_read_increments_counter(client):
    secret_id = _post_secret(client).get_json()["id"]
    before = _val("vanishd_secrets_read_total")
    resp = client.get(f"/api/secrets/{secret_id}")
    assert resp.status_code == 200
    assert _val("vanishd_secrets_read_total") - before == 1.0


def test_not_found_increments_counter(client):
    before = _val("vanishd_secrets_not_found_total")
    resp = client.get("/api/secrets/nonexistent-id")
    assert resp.status_code == 404
    assert _val("vanishd_secrets_not_found_total") - before == 1.0


def test_cleanup_increments_expired_counter(app):
    import app.db as db
    from app.cleanup import cleanup_once

    now = int(time.time())
    conn = db.get_db()
    conn.execute(
        "INSERT INTO secrets (id, ciphertext, iv, salt, created_at, expires_at) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        ("exp1", "ct", "iv", None, now - 200, now - 1),
    )
    conn.execute(
        "INSERT INTO secrets (id, ciphertext, iv, salt, created_at, expires_at) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        ("exp2", "ct", "iv", None, now - 200, now - 1),
    )
    conn.commit()
    conn.close()

    before = _val("vanishd_secrets_expired_total")
    cleanup_once()
    assert _val("vanishd_secrets_expired_total") - before == 2.0


def test_metrics_endpoint_returns_prometheus_format(client):
    _post_secret(client)
    resp = client.get("/metrics")
    assert resp.status_code == 200
    assert b"vanishd_secrets_created_total" in resp.data
    assert b"TYPE vanishd_secrets_created_total counter" in resp.data


def test_request_duration_histogram_recorded(client):
    _post_secret(client)
    count = REGISTRY.get_sample_value(
        "vanishd_request_duration_seconds_count",
        {"route": "/api/secrets", "method": "POST"},
    )
    assert count is not None and count >= 1.0
