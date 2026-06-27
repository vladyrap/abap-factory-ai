"""Espera a que la base de datos esté disponible antes de arrancar (robustez en Docker/prod)."""
from __future__ import annotations
import logging
import time
from sqlalchemy import text

logger = logging.getLogger(__name__)


def wait_for_db(engine, retries: int = 30, delay: float = 1.0) -> bool:
    """Intenta 'SELECT 1' hasta que responda. Devuelve True si conectó."""
    for attempt in range(1, retries + 1):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception as exc:  # noqa: BLE001
            logger.warning("db_wait: BD no lista (intento %s/%s): %s", attempt, retries, str(exc)[:120])
            time.sleep(delay)
    logger.error("db_wait: la base de datos no respondió tras %s intentos", retries)
    return False
