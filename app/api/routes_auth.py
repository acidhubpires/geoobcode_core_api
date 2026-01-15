from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.domain.schemas import LoginRequest, TokenResponse
from app.core.security import create_access_token
from app.infra.json_store import JsonStore

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, store: JsonStore = Depends(JsonStore)):
    user = store.authenticate(body.tenant_id, body.email, body.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas")

    token = create_access_token(
        {"tenant_id": user["tenant_id"], "user_id": user["id"], "email": user["email"], "role": user.get("role", "user")}
    )
    return TokenResponse(access_token=token)
