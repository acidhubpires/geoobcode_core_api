from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routes_auth import router as auth_router
from app.api.routes_agents import router as agents_router
from app.api.routes_chat import router as chat_router
from app.api.routes_admin import router as admin_router

app = FastAPI(
    title="Blue Identy Agents AI — GeoOBCode Core API",
    version="0.1.0",
    description="""
    Blue Identy Agents AI é uma camada de agentes cognitivos
    construída sobre o GeoOBCode Core API.

    Esta API fornece infraestrutura para identidade,
    governança, selagem e verificação de estados e eventos,
    com foco em ambientes corporativos e regulados.
    """,
)

if settings.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(auth_router)
app.include_router(agents_router)
app.include_router(chat_router)
app.include_router(admin_router)
