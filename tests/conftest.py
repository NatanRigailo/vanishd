import pytest

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
