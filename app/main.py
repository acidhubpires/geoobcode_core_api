from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse
from fastapi.openapi.docs import get_swagger_ui_html

from app.core.config import settings
from app.api.routes_auth import router as auth_router
from app.api.routes_agents import router as agents_router
from app.api.routes_chat import router as chat_router
from app.api.routes_admin import router as admin_router

# Paths
ROOT_DIR = Path(__file__).resolve().parents[1]  # geoobcode_core_api/
ASSETS_DIR = ROOT_DIR / "assets"

# 1) cria o app PRIMEIRO
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
    docs_url=None,   # desliga /docs padrão
    redoc_url=None,  # opcional: desliga /redoc padrão
)

# 2) assets (monta uma vez só, e só se existir)
if ASSETS_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")


@app.get("/docs", include_in_schema=False)
def custom_swagger_ui_html():
    swagger = get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} — Swagger UI",
        swagger_favicon_url="/assets/branding/blue-identity-logo.png",
    )

    logo_header = """
    <div style="
        display:flex;
        align-items:center;
        gap:16px;
        padding:12px 24px;
        border-bottom:1px solid #eee;
        background:#fff;
    ">
      <img src="/assets/branding/blue-identity-logo.png" alt="Blue Identy" style="height:120px;" />
      <div style="line-height:1.2">
        <div style="font-size:12px;font-weight:600;">Powered By</div>
        <div style="font-size:18px;color:#666;">Ariadny Tecnology / PIRESAAO - 2026</div>
      </div>
    </div>
    """

    html = swagger.body.decode("utf-8")
    html = html.replace("<body>", "<body>" + logo_header, 1)
    return HTMLResponse(html)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # opcional (Swagger UI nem sempre usa x-logo; ReDoc costuma respeitar mais)
    schema.setdefault("info", {})
    schema["info"]["x-logo"] = {
        "url": "/assets/branding/blue-identity-logo.png",
        "altText": "Blue Identy Agents AI",
    }

    app.openapi_schema = schema
    return app.openapi_schema


app.openapi = custom_openapi

# 3) CORS
if settings.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# 4) routers
app.include_router(auth_router)
app.include_router(agents_router)
app.include_router(chat_router)
app.include_router(admin_router)
