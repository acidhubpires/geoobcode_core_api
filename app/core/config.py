from __future__ import annotations

import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()


class Settings(BaseModel):
    groq_api_key: str = Field(default_factory=lambda: os.getenv("GROQ_API_KEY", ""))
    synth_model: str = Field(default_factory=lambda: os.getenv("SYNTH_MODEL", "llama-3.3-70b-versatile"))
    chat_model: str = Field(default_factory=lambda: os.getenv("CHAT_MODEL", "llama-3.3-70b-versatile"))

    jwt_secret: str = Field(default_factory=lambda: os.getenv("JWT_SECRET", ""))
    jwt_issuer: str = Field(default_factory=lambda: os.getenv("JWT_ISSUER", "acid_agentia_hub"))
    jwt_expires_min: int = Field(default_factory=lambda: int(os.getenv("JWT_EXPIRES_MIN", "240")))

    max_total_chars: int = Field(default_factory=lambda: int(os.getenv("MAX_TOTAL_CHARS", "120000")))
    chunk_chars: int = Field(default_factory=lambda: int(os.getenv("CHUNK_CHARS", "12000")))
    max_partials: int = Field(default_factory=lambda: int(os.getenv("MAX_PARTIALS", "12")))
    max_history_msgs: int = Field(default_factory=lambda: int(os.getenv("MAX_HISTORY_MSGS", "12")))

    cors_origins: list[str] = Field(
        default_factory=lambda: [o.strip() for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()]
    )


settings = Settings()
