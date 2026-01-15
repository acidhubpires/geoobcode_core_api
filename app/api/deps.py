from __future__ import annotations

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.security import decode_access_token
from app.infra.json_store import JsonStore

auth_scheme = HTTPBearer(auto_error=True)


def get_store() -> JsonStore:
    return JsonStore()


def get_current_user(creds: HTTPAuthorizationCredentials = Depends(auth_scheme)) -> dict:
    return decode_access_token(creds.credentials)
