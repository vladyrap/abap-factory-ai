"""Manejo global de errores y middleware de observabilidad.

Asegura respuestas JSON limpias (sin stack traces filtrados al cliente), traduce
errores conocidos a códigos HTTP correctos y registra cada request con un id.
"""
from __future__ import annotations
import logging
import time
import uuid

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.services.ai.engine import AIDisabledError, CostLimitError

logger = logging.getLogger("abapfactory")


def register(app: FastAPI) -> None:
    @app.exception_handler(AIDisabledError)
    async def _ai_disabled(request: Request, exc: AIDisabledError):
        return JSONResponse(status_code=503, content={"detail": str(exc)})

    @app.exception_handler(CostLimitError)
    async def _cost_limit(request: Request, exc: CostLimitError):
        return JSONResponse(status_code=429, content={"detail": str(exc)})

    @app.exception_handler(SQLAlchemyError)
    async def _db_error(request: Request, exc: SQLAlchemyError):
        rid = getattr(request.state, "request_id", "-")
        logger.exception("db.error", extra={"request_id": rid})
        return JSONResponse(status_code=500, content={
            "detail": "Error de base de datos. El equipo fue notificado.", "request_id": rid})

    @app.exception_handler(Exception)
    async def _unhandled(request: Request, exc: Exception):
        rid = getattr(request.state, "request_id", "-")
        logger.exception("unhandled.error", extra={"request_id": rid})
        return JSONResponse(status_code=500, content={
            "detail": "Error interno. Inténtalo de nuevo.", "request_id": rid})

    @app.middleware("http")
    async def _observe(request: Request, call_next):
        rid = request.headers.get("X-Request-ID") or uuid.uuid4().hex[:12]
        request.state.request_id = rid
        t0 = time.time()
        try:
            response = await call_next(request)
        except Exception:
            # Lo capturan los exception handlers; aquí solo medimos.
            raise
        ms = int((time.time() - t0) * 1000)
        response.headers["X-Request-ID"] = rid
        if request.url.path not in ("/health", "/metrics"):
            logger.info("http", extra={"request_id": rid, "method": request.method,
                                       "path": request.url.path, "status": response.status_code, "ms": ms})
        # Auditoría de acciones mutantes (no rompe el request si falla)
        try:
            from app.services.audit import record_request
            record_request(
                request.method, request.url.path, response.status_code,
                request.headers.get("Authorization"), rid,
                request.client.host if request.client else None,
            )
        except Exception:  # noqa: BLE001
            pass
        return response
