import os
from dataclasses import dataclass

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError
from jwt import PyJWKClient


bearer_scheme = HTTPBearer(auto_error=False)


@dataclass
class AuthenticatedUser:
    sub: str
    claims: dict


def _as_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _is_auth_required() -> bool:
    has_cognito_config = bool(os.getenv("COGNITO_ISSUER") and os.getenv("COGNITO_CLIENT_ID"))
    default_required = os.getenv("APP_ENV", "development").lower() == "production" or has_cognito_config
    return _as_bool(os.getenv("AUTH_REQUIRED"), default_required)


def _resolve_signing_key(token: str, issuer: str):
    jwks_url = f"{issuer.rstrip('/')}/.well-known/jwks.json"
    jwk_client = PyJWKClient(jwks_url)
    signing_key = jwk_client.get_signing_key_from_jwt(token)
    return signing_key.key, "RS256"


def _validate_audience(claims: dict, client_id: str) -> None:
    token_use = claims.get("token_use")
    if token_use == "id":
        if claims.get("aud") != client_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="aud inválido")
        return

    if token_use == "access":
        token_client = claims.get("client_id") or claims.get("aud")
        if token_client != client_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="client_id inválido")
        return

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="token_use inválido")


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> AuthenticatedUser:
    if not _is_auth_required():
        return AuthenticatedUser(sub="anonymous", claims={"auth_required": False})

    issuer = os.getenv("COGNITO_ISSUER")
    client_id = os.getenv("COGNITO_CLIENT_ID")
    if not issuer or not client_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Configuração de autenticação incompleta",
        )

    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token Bearer obrigatório",
        )

    token = credentials.credentials
    try:
        public_key, algorithm = _resolve_signing_key(token, issuer)
        claims = jwt.decode(
            token,
            public_key,
            algorithms=[algorithm],
            issuer=issuer,
            options={"verify_aud": False},
        )
        _validate_audience(claims, client_id)
    except HTTPException:
        raise
    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Falha na validação do token")

    sub = claims.get("sub")
    if not sub:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token sem sub")

    return AuthenticatedUser(sub=str(sub), claims=claims)


def enforce_same_user(requested_user_id: int, current_user: AuthenticatedUser) -> None:
    if not _is_auth_required():
        return

    claim_user_id = (
        current_user.claims.get("custom:user_id")
        or current_user.claims.get("user_id")
    )

    if claim_user_id is None and str(current_user.sub).isdigit():
        claim_user_id = current_user.sub

    if claim_user_id is None:
        return

    if str(requested_user_id) != str(claim_user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado para este usuário",
        )
