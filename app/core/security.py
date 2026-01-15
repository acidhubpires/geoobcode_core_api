from __future__ import annotations

import time
from typing import Any, Dict

import jwt
from fastapi import HTTPException, status
from passlib.context import CryptContext

from app.core.config import settings

# PBKDF2: estável no Windows, sem limite 72 bytes e sem conflito bcrypt/passlib
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def create_access_token(payload: Dict[str, Any]) -> str:
    if not settings.jwt_secret:
        raise RuntimeError("JWT_SECRET não definido no .env.")
    now = int(time.time())
    exp = now + int(settings.jwt_expires_min) * 60
    token_payload = {**payload, "iss": settings.jwt_issuer, "iat": now, "exp": exp}
    return jwt.encode(token_payload, settings.jwt_secret, algorithm="HS256")


def decode_access_token(token: str) -> Dict[str, Any]:
    if not settings.jwt_secret:
        raise RuntimeError("JWT_SECRET não definido no .env.")
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=["HS256"], issuer=settings.jwt_issuer)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
