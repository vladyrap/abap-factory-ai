"""Generador de especificación técnica — Módulo 3."""
from __future__ import annotations
from sqlalchemy.orm import Session

from app.services.ai.engine import run_agent, parse_json
from app.services.ai.agents import json_instruction

_SCHEMA = (
    '{"functional_description": "...", "technical_objective": "...", '
    '"assumptions": ["..."], "sap_objects": ["..."], "standard_tables": ["..."], '
    '"suggested_bapis": ["..."], "badis_user_exits": ["..."], "risks": ["..."], '
    '"dependencies": ["..."], "performance_notes": "...", "security_notes": "...", '
    '"transport_plan": "...", "rollback_plan": "...", "raw_markdown": "<spec completa en markdown>"}'
)


def generate_spec(
    db: Session,
    *,
    description: str,
    sap_context: dict,
    project_id: int | None = None,
    user_id: int | None = None,
):
    agent_key = "abap_s4" if str(sap_context.get("sap_version", "")).upper().startswith("S4") else "abap_ecc"
    ctx_lines = "\n".join(f"- {k}: {v}" for k, v in sap_context.items() if v)
    prompt = (
        "Elabora una especificación técnica profesional y completa para el siguiente "
        "requerimiento de desarrollo SAP.\n\n"
        f"# Contexto SAP\n{ctx_lines}\n\n# Requerimiento\n{description}\n\n"
        + json_instruction(_SCHEMA)
    )
    result = run_agent(db, agent_key, prompt, operation="spec", project_id=project_id, user_id=user_id)
    data = parse_json(result.text)
    data["_meta"] = {"provider": result.provider, "model": result.model}
    return data
