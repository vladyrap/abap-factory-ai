"""Crea los roles base del sistema (idempotente). Se ejecuta al iniciar la app."""
from __future__ import annotations
import logging
from app.core.database import SessionLocal
from app.core.permissions import LEGACY_ROLE_PERMS
from app.models.role import Role

logger = logging.getLogger(__name__)

_SYSTEM_ROLES = [
    ("Administrador", "admin", "Acceso total al sistema"),
    ("Líder técnico", "tech_lead", "Genera, aprueba y ve costos"),
    ("Consultor ABAP", "consultant", "Genera y edita desarrollos"),
    ("QA", "qa", "Pruebas y revisión de calidad"),
    ("Cliente (solo lectura)", "client_readonly", "Solo lectura y exportación"),
]


def ensure_system_roles() -> None:
    db = SessionLocal()
    try:
        for name, legacy_key, desc in _SYSTEM_ROLES:
            if db.query(Role).filter(Role.name == name).first():
                continue
            db.add(Role(name=name, description=desc, is_system=True,
                        permissions=list(LEGACY_ROLE_PERMS.get(legacy_key, []))))
        db.commit()
    except Exception:  # noqa: BLE001
        logger.exception("role_seed.failed")
        db.rollback()
    finally:
        db.close()
