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
)

setup_logging()

if not os.getenv("TESTING"):
    Base.metadata.create_all(bind=engine)
    from app.services import scheduler
    scheduler.start()

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

for r in (auth, admin, clients, projects, catalog, generation, dumps, inspector,
          tests, dashboard, costs, agents, exports, jobs, recipes, knowledge):
    app.include_router(r.router, prefix=settings.API_PREFIX)


@app.get("/health")
def health():
    from app.services.ai.provider import get_provider
    return {
        "status": "ok",
        "version": settings.VERSION,
        "ai_providers": {
            "claude": get_provider("claude").is_enabled(),
            "openai": get_provider("openai").is_enabled(),
        },
    }
