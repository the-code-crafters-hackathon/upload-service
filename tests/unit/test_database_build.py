import importlib
import os
import pytest


def test_build_db_url_with_database_url(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    mod = importlib.import_module("app.infrastructure.db.database")
    importlib.reload(mod)
    assert mod._build_db_url() == "sqlite:///:memory:"


def test_build_db_url_raises_when_no_env(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("SQLALCHEMY_DATABASE_URL", raising=False)
    monkeypatch.delenv("DB_SECRET_NAME", raising=False)

    import importlib

    with pytest.raises(RuntimeError):
        importlib.reload(importlib.import_module("app.infrastructure.db.database"))
