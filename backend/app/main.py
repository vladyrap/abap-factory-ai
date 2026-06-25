import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import Base, engine
from app.core.logging_config import setup_logging
import app.models  # noqa: F401 — registra todos los modelos en Base.metadata
from app.api.routes import (
    auth, admin, clients, projects, catalog, generation, dumps, inspector,
    tests, dashboard, costs, agents, exports, jobs, recipes, knowledge,
    migration, naming, dev_docs, connections, solution, roles, audit,
)

setup_logging()

import logging
_log = logging.getLogger("abapfactory")

# Endurecimiento: no arrancar en producción con la SECRET_KEY por defecto.
if settings.ENV == "prod" and "change-me" in settings.SECRET_KEY:
    raise RuntimeError("SECRET_KEY por defecto en producción. Define una SECRET_KEY robusta en .env.prod.")

if not os.getenv("TESTING"):
    Base.metadata.create_all(bind=engine)
    # Auto-migración aditiva: agrega columnas nuevas a tablas existentes sin recrear la BD
    from app.core.schema_guard import ensure_columns
    ensure_columns()
    from app.services import scheduler
    scheduler.start()
    from app.services.role_seed import ensure_system_roles
    ensure_system_roles()
    from app.services.agent_seed import ensure_system_agents
    ensure_system_agents()

    # Avisos de configuración (no bloquean el arranque)
    from app.services.ai.provider import any_enabled
    if not any_enabled():
        _log.warning("config: ningún proveedor de IA configurado (ANTHROPIC/OPENAI/GEMINI). Endpoints IA → 503.")
    if settings.ENV == "prod" and any("localhost" in o for o in settings.CORS_ORIGINS):
        _log.warning("config: CORS incluye localhost en producción. Revisa CORS_ORIGINS.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Manejo global de errores + logging con request-id
from app.core.errors import register as register_errors
register_errors(app)

for r in (auth, admin, clients, projects, catalog, generation, dumps, inspector,
          tests, dashboard, costs, agents, exports, jobs, recipes, knowledge,
          migration, naming, dev_docs, connections, solution, roles, audit):
    app.include_router(r.router, prefix=settings.API_PREFIX)


@app.get("/health")
def health():
    from app.services.ai.provider import get_provider
    from sqlalchemy import text
    from app.core.database import SessionLocal

    db_ok = True
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
    except Exception:  # noqa: BLE001
        db_ok = False

    return {
        "status": "ok" if db_ok else "degraded",
        "version": settings.VERSION,
        "database": "up" if db_ok else "down",
        "ai_providers": {
            "claude": get_provider("claude").is_enabled(),
            "openai": get_provider("openai").is_enabled(),
            "gemini": get_provider("gemini").is_enabled(),
        },
    }
