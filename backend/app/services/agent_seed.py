"""Siembra en BD los agentes base del catálogo en código (idempotente).

Así los 7 agentes aparecen como filas editables y conviven con los agentes
personalizados que cree el usuario desde la pantalla de Agentes IA.
"""
from __future__ import annotations
import logging
from app.core.database import SessionLocal
from app.models.agent_config import AgentConfig
from app.services.ai.agents import AGENTS

logger = logging.getLogger(__name__)


def ensure_system_agents() -> None:
    db = SessionLocal()
    try:
        for key, a in AGENTS.items():
            if db.query(AgentConfig).filter(AgentConfig.agent_key == key).first():
                continue
            db.add(AgentConfig(
                agent_key=key, name=a.name, description=a.description,
                provider=a.default_provider, model=a.default_model,
                temperature=a.default_temperature, max_tokens=a.default_max_tokens,
                system_prompt=a.system_prompt, is_active=True, is_system=True,
            ))
        db.commit()
    except Exception:  # noqa: BLE001
        logger.exception("agent_seed.failed")
        db.rollback()
    finally:
        db.close()
