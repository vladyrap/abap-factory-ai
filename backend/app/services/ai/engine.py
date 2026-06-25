"""Orquestador de agentes IA.

`run_agent()` resuelve la configuración efectiva del agente (BD AgentConfig > catálogo en
código), llama al proveedor conmutable, registra el consumo en AIUsage y devuelve el resultado.
Todos los servicios de módulo (generator, dump_solver, ...) pasan por aquí.
"""
from __future__ import annotations
import json
import logging
import re
from typing import Optional

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.agent_config import AgentConfig
from app.models.ai_usage import AIUsage
from app.services.ai import pricing
from app.services.ai.agents import get_agent, Agent
from app.services.ai.provider import get_provider, LLMResult, any_enabled

logger = logging.getLogger(__name__)


class AIDisabledError(RuntimeError):
    """Ningún proveedor de IA tiene API key configurada."""


class CostLimitError(RuntimeError):
    """Se superó el límite diario de costo de IA configurado para el usuario."""


def _check_cost_limit(db: Session, user_id: int | None) -> None:
    limit = getattr(settings, "DAILY_AI_COST_LIMIT_USD", 0) or 0
    if limit <= 0 or not user_id:
        return
    from datetime import datetime
    from sqlalchemy import func
    start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    spent = (
        db.query(func.coalesce(func.sum(AIUsage.cost_usd), 0.0))
        .filter(AIUsage.user_id == user_id, AIUsage.created_at >= start)
        .scalar()
    ) or 0.0
    if spent >= limit:
        raise CostLimitError(
            f"Límite diario de IA alcanzado (${spent:.2f} de ${limit:.2f}). Intenta mañana o ajusta el límite."
        )


def _effective_config(db: Session, agent: Agent) -> tuple[str, str | None, float, int, str]:
    """Devuelve (provider, model, temperature, max_tokens, system_prompt) efectivos."""
    cfg = db.query(AgentConfig).filter(AgentConfig.agent_key == agent.key).first()
    if cfg and cfg.is_active:
        return (
            cfg.provider or agent.default_provider,
            cfg.model or agent.default_model,
            cfg.temperature if cfg.temperature is not None else agent.default_temperature,
            cfg.max_tokens or agent.default_max_tokens,
            cfg.system_prompt or agent.system_prompt,
        )
    return (
        agent.default_provider,
        agent.default_model,
        agent.default_temperature,
        agent.default_max_tokens,
        agent.system_prompt,
    )


def run_agent(
    db: Session,
    agent_key: str,
    user_prompt: str,
    *,
    operation: str,
    project_id: Optional[int] = None,
    user_id: Optional[int] = None,
    provider_override: Optional[str] = None,
    model_override: Optional[str] = None,
    extra_system: str = "",
) -> LLMResult:
    """Ejecuta un agente y registra el consumo. Lanza AIDisabledError si no hay proveedor."""
    if not any_enabled():
        raise AIDisabledError(
            "No hay proveedor de IA configurado. Define ANTHROPIC_API_KEY u OPENAI_API_KEY."
        )

    _check_cost_limit(db, user_id)

    agent = get_agent(agent_key)
    provider_name, model, temperature, max_tokens, system_prompt = _effective_config(db, agent)
    provider_name = provider_override or provider_name
    model = model_override or model

    provider = get_provider(provider_name)
    # Si el proveedor elegido no tiene key, caer a cualquiera habilitado
    # (priorizando el DEFAULT_AI_PROVIDER configurado).
    if not provider.is_enabled():
        for cand in [settings.DEFAULT_AI_PROVIDER, "gemini", "claude", "openai"]:
            p = get_provider(cand)
            if p.is_enabled():
                provider = p
                provider_name = p.name
                model = None  # usar el modelo por defecto del proveedor de fallback
                break

    system = system_prompt + (("\n\n" + extra_system) if extra_system else "")
    result = provider.complete(
        system=system,
        user_prompt=user_prompt,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
    )

    usd = pricing.cost_usd(result.model, result.tokens_in, result.tokens_out)
    usage = AIUsage(
        project_id=project_id,
        user_id=user_id,
        operation=operation,
        agent_key=agent_key,
        provider=result.provider,
        model=result.model,
        tokens_in=result.tokens_in,
        tokens_out=result.tokens_out,
        cost_usd=usd,
        cost_clp=pricing.cost_clp(usd),
        latency_ms=result.latency_ms,
    )
    db.add(usage)
    db.commit()
    return result


def parse_json(text: str) -> dict:
    """Extrae un objeto JSON de la respuesta del modelo, tolerante a fences markdown."""
    cleaned = text.strip()
    # quitar fences ```json ... ```
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # rescatar el primer bloque { ... } balanceado
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
    logger.warning("ai.parse_json_failed")
    return {}
