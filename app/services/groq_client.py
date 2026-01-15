from __future__ import annotations

from typing import List, Dict
from groq import Groq

from app.core.config import settings


def make_client() -> Groq:
    if not settings.groq_api_key:
        raise RuntimeError("GROQ_API_KEY não definido no .env.")
    return Groq(api_key=settings.groq_api_key)


def chat_completion(
    client: Groq,
    model: str,
    messages: List[Dict[str, str]],
    temperature: float = 0.2,
    max_tokens: int = 2048,
) -> str:
    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return (resp.choices[0].message.content or "").strip()
