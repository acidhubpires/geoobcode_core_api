from __future__ import annotations

from fastapi import APIRouter
from app.domain.schemas import HealthResponse

router = APIRouter(tags=["admin"])


@router.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse()
