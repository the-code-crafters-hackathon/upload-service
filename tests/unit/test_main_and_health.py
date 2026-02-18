from unittest.mock import Mock


def test_main_includes_routers():
    import app.main  # noqa: F401
    from app.infrastructure.api.fastapi import app

    paths = {route.path for route in app.routes}
    assert "/health/" in paths
    assert "/health/db" in paths
    assert "/upload/video" in paths


def test_health_check_returns_ok():
    from app.api.check import health_check

    assert health_check() == {"status": "ok"}


def test_health_db_check_returns_connected():
    from app.api.check import health_db_check

    assert health_db_check(db=Mock()) == {"status": "connected"}
