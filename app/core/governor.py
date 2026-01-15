from __future__ import annotations

from dataclasses import dataclass
from fastapi import HTTPException, status

from app.core.config import settings


@dataclass
class Budgets:
    max_total_chars: int
    chunk_chars: int
    max_partials: int
    max_history_msgs: int


def get_budgets() -> Budgets:
    return Budgets(
        max_total_chars=settings.max_total_chars,
        chunk_chars=settings.chunk_chars,
        max_partials=settings.max_partials,
        max_history_msgs=settings.max_history_msgs,
    )


def enforce_max_chars(text: str, limit: int, name: str) -> str:
    if text is None:
        return ""
    t = text.strip()
    if len(t) > limit:
        return t[:limit]
    return t


def guard_payload_size(total_chars: int) -> None:
    if total_chars > settings.max_total_chars * 2:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Payload grande demais. Reduza documentos/URLs ou divida em lotes.",
        )
