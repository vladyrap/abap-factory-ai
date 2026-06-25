"""Auditoría de acciones: registra requests mutantes con el usuario que las hizo."""
from __future__ import annotations
import logging

from app.core.database import SessionLocal
from app.core.security import decode_token
from app.models.audit_log import AuditLog
from app.models.user import User

logger = logging.getLogger(__name__)

_MUTATING = {"POST", "PUT", "PATCH", "DELETE"}

# Etiquetas legibles para rutas conocidas (acción de negocio).
_ACTION_HINTS = [
    ("/generation/code", "Generó código"),
    ("/generation/artifacts", "Editó/aprobó artefacto"),
    ("/solution/build", "Resolvió requerimiento"),
    ("/migration/migrate", "Migró código"),
    ("/dumps/analyze", "Analizó dump"),
    ("/inspector/inspect", "Inspeccionó código"),
    ("/tests/", "Generó pruebas"),
    ("/dev-docs/generate", "Generó documento técnico"),
    ("/roles", "Gestionó roles"),
    ("/admin/users", "Gestionó usuarios"),
    ("/auth/login", "Inició sesión"),
    ("/projects", "Gestionó proyecto"),
    ("/clients", "Gestionó cliente"),
    ("/naming", "Configuró nomenclatura"),
    ("/knowledge", "Cargó memoria de cliente"),
]


def _action_for(path: str) -> str:
    for frag, label in _ACTION_HINTS:
        if frag in path:
            return label
    return "Acción"


def record_request(method: str, path: str, status: int, auth_header: str | None,
                   request_id: str, ip: str | None) -> None:
    """Crea una entrada de auditoría. Abre su propia sesión; nunca rompe el request."""
    if method not in _MUTATING:
        return
    if not path.startswith("/api") or "/audit" in path:
        return
    db = SessionLocal()
    try:
        user_id, email = None, None
        if auth_header and auth_header.lower().startswith("bearer "):
            payload = decode_token(auth_header.split(" ", 1)[1])
            if payload:
                user_id = payload.get("sub")
                u = db.query(User).filter(User.id == user_id).first() if user_id else None
                email = u.email if u else None
        db.add(AuditLog(
            user_id=int(user_id) if user_id else None, user_email=email,
            method=method, path=path, status=status, action=_action_for(path),
            request_id=request_id, ip=ip,
        ))
        db.commit()
    except Exception:  # noqa: BLE001
        logger.exception("audit.record_failed")
        db.rollback()
    finally:
        db.close()
