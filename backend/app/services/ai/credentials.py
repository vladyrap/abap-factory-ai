"""Credenciales de IA gestionables desde la web (cifradas en BD) con fallback a env.

El admin puede cargar las API keys desde la pantalla de Credenciales IA. Se guardan
cifradas (Fernet derivado de SECRET_KEY). Al leerlas se prioriza la BD; si no hay,
se usa la variable de entorno. Nunca se devuelve el valor en claro al frontend.
"""
from __future__ import annotations
import base64
import hashlib
import logging
from typing import Optional

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal

logger = logging.getLogger(__name__)

PROVIDERS = ("anthropic", "openai", "gemini")
_SETTING = {"anthropic": "ANTHROPIC_API_KEY", "openai": "OPENAI_API_KEY", "gemini": "GEMINI_API_KEY"}
_DEFAULT_KEY = "DEFAULT_AI_PROVIDER"


def _fernet():
    from cryptography.fernet import Fernet
    digest = hashlib.sha256(settings.SECRET_KEY.encode()).digest()
    return Fernet(base64.urlsafe_b64encode(digest))


def _encrypt(plain: str) -> str:
    return _fernet().encrypt(plain.encode()).decode()


def _decrypt(token: str) -> Optional[str]:
    try:
        return _fernet().decrypt(token.encode()).decode()
    except Exception:  # noqa: BLE001 — token corrupto o SECRET_KEY cambiada
        logger.warning("credentials.decrypt_failed")
        return None


def _db_value(name: str) -> Optional[str]:
    """Lee un AppSetting (descifrado) de forma resiliente (tabla puede no existir)."""
    try:
        db = SessionLocal()
        try:
            from app.models.app_setting import AppSetting
            row = db.query(AppSetting).filter(AppSetting.key == name).first()
            if row and row.value:
                return _decrypt(row.value) if row.is_secret else row.value
        finally:
            db.close()
    except Exception:  # noqa: BLE001 — BD no lista / tabla ausente
        pass
    return None


def get_key(provider: str) -> Optional[str]:
    """API key efectiva del proveedor: BD primero, luego variable de entorno."""
    name = _SETTING.get(provider)
    if not name:
        return None
    val = _db_value(name)
    if val:
        return val
    env = getattr(settings, name, None)
    return env or None


def key_source(provider: str) -> Optional[str]:
    name = _SETTING.get(provider)
    if name and _db_value(name):
        return "bd"
    if name and getattr(settings, name, None):
        return "env"
    return None


def masked(provider: str) -> Optional[str]:
    k = get_key(provider)
    if not k:
        return None
    return f"••••{k[-4:]}" if len(k) >= 4 else "••••"


def default_provider() -> str:
    return _db_value(_DEFAULT_KEY) or settings.DEFAULT_AI_PROVIDER


def set_key(db: Session, provider: str, value: Optional[str]) -> None:
    """Guarda (cifrada) o limpia la key del proveedor."""
    name = _SETTING.get(provider)
    if not name:
        return
    _upsert(db, name, _encrypt(value) if value else None, is_secret=1)


def set_default_provider(db: Session, provider: str) -> None:
    if provider in PROVIDERS:
        _upsert(db, _DEFAULT_KEY, provider, is_secret=0)


def _upsert(db: Session, key: str, value: Optional[str], is_secret: int) -> None:
    from app.models.app_setting import AppSetting
    row = db.query(AppSetting).filter(AppSetting.key == key).first()
    if not row:
        row = AppSetting(key=key)
        db.add(row)
    row.value = value
    row.is_secret = is_secret
    db.commit()
