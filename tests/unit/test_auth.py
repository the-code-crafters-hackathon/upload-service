import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from jwt import InvalidTokenError

from app.infrastructure.security import auth


def _bearer(token: str = "token") -> HTTPAuthorizationCredentials:
    return HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)


def test_as_bool_and_is_auth_required(monkeypatch):
    assert auth._as_bool("true", False) is True
    assert auth._as_bool("0", True) is False
    assert auth._as_bool(None, True) is True

    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.delenv("AUTH_REQUIRED", raising=False)
    assert auth._is_auth_required() is True

    monkeypatch.setenv("AUTH_REQUIRED", "false")
    assert auth._is_auth_required() is False

    monkeypatch.delenv("AUTH_REQUIRED", raising=False)
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("COGNITO_ISSUER", "https://issuer")
    monkeypatch.setenv("COGNITO_CLIENT_ID", "client")
    assert auth._is_auth_required() is True


def test_validate_audience_variants():
    auth._validate_audience({"token_use": "id", "aud": "abc"}, "abc")
    auth._validate_audience({"token_use": "access", "client_id": "abc"}, "abc")
    auth._validate_audience({"token_use": "access", "aud": "abc"}, "abc")

    with pytest.raises(HTTPException) as exc_aud:
        auth._validate_audience({"token_use": "id", "aud": "x"}, "abc")
    assert exc_aud.value.status_code == 401

    with pytest.raises(HTTPException) as exc_client:
        auth._validate_audience({"token_use": "access", "client_id": "x"}, "abc")
    assert exc_client.value.status_code == 401

    with pytest.raises(HTTPException) as exc_use:
        auth._validate_audience({"token_use": "refresh"}, "abc")
    assert exc_use.value.status_code == 401


def test_get_current_user_auth_disabled(monkeypatch):
    monkeypatch.setenv("AUTH_REQUIRED", "false")

    user = auth.get_current_user(None)

    assert user.sub == "anonymous"
    assert user.claims["auth_required"] is False


def test_get_current_user_missing_config(monkeypatch):
    monkeypatch.setenv("AUTH_REQUIRED", "true")
    monkeypatch.delenv("COGNITO_ISSUER", raising=False)
    monkeypatch.delenv("COGNITO_CLIENT_ID", raising=False)

    with pytest.raises(HTTPException) as exc:
        auth.get_current_user(_bearer())

    assert exc.value.status_code == 500


def test_get_current_user_missing_credentials(monkeypatch):
    monkeypatch.setenv("AUTH_REQUIRED", "true")
    monkeypatch.setenv("COGNITO_ISSUER", "https://issuer")
    monkeypatch.setenv("COGNITO_CLIENT_ID", "client")

    with pytest.raises(HTTPException) as exc:
        auth.get_current_user(None)

    assert exc.value.status_code == 401


def test_get_current_user_invalid_token_error(monkeypatch):
    monkeypatch.setenv("AUTH_REQUIRED", "true")
    monkeypatch.setenv("COGNITO_ISSUER", "https://issuer")
    monkeypatch.setenv("COGNITO_CLIENT_ID", "client")
    monkeypatch.setattr(auth, "_resolve_signing_key", lambda *_: ("key", "RS256"))

    def _raise_invalid(*_args, **_kwargs):
        raise InvalidTokenError("bad")

    monkeypatch.setattr(auth.jwt, "decode", _raise_invalid)

    with pytest.raises(HTTPException) as exc:
        auth.get_current_user(_bearer())

    assert exc.value.status_code == 401
    assert "Token inválido" in exc.value.detail


def test_get_current_user_unexpected_validation_error(monkeypatch):
    monkeypatch.setenv("AUTH_REQUIRED", "true")
    monkeypatch.setenv("COGNITO_ISSUER", "https://issuer")
    monkeypatch.setenv("COGNITO_CLIENT_ID", "client")

    def _raise_any(*_args, **_kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(auth, "_resolve_signing_key", _raise_any)

    with pytest.raises(HTTPException) as exc:
        auth.get_current_user(_bearer())

    assert exc.value.status_code == 401
    assert "Falha na validação" in exc.value.detail


def test_get_current_user_missing_sub(monkeypatch):
    monkeypatch.setenv("AUTH_REQUIRED", "true")
    monkeypatch.setenv("COGNITO_ISSUER", "https://issuer")
    monkeypatch.setenv("COGNITO_CLIENT_ID", "client")
    monkeypatch.setattr(auth, "_resolve_signing_key", lambda *_: ("key", "RS256"))
    monkeypatch.setattr(auth.jwt, "decode", lambda *_args, **_kwargs: {"token_use": "id", "aud": "client"})

    with pytest.raises(HTTPException) as exc:
        auth.get_current_user(_bearer())

    assert exc.value.status_code == 401
    assert "Token sem sub" in exc.value.detail


def test_get_current_user_success(monkeypatch):
    monkeypatch.setenv("AUTH_REQUIRED", "true")
    monkeypatch.setenv("COGNITO_ISSUER", "https://issuer")
    monkeypatch.setenv("COGNITO_CLIENT_ID", "client")
    monkeypatch.setattr(auth, "_resolve_signing_key", lambda *_: ("key", "RS256"))
    monkeypatch.setattr(
        auth.jwt,
        "decode",
        lambda *_args, **_kwargs: {"sub": "42", "token_use": "id", "aud": "client", "custom:user_id": "42"},
    )

    user = auth.get_current_user(_bearer())

    assert user.sub == "42"
    assert user.claims["custom:user_id"] == "42"


def test_enforce_same_user_rules(monkeypatch):
    monkeypatch.setenv("AUTH_REQUIRED", "false")
    auth.enforce_same_user(10, auth.AuthenticatedUser(sub="x", claims={}))

    monkeypatch.setenv("AUTH_REQUIRED", "true")
    auth.enforce_same_user(10, auth.AuthenticatedUser(sub="x", claims={}))
    auth.enforce_same_user(10, auth.AuthenticatedUser(sub="10", claims={}))
    auth.enforce_same_user(10, auth.AuthenticatedUser(sub="x", claims={"custom:user_id": "10"}))

    with pytest.raises(HTTPException) as exc:
        auth.enforce_same_user(10, auth.AuthenticatedUser(sub="x", claims={"user_id": "11"}))

    assert exc.value.status_code == 403
