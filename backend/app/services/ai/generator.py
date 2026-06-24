"""Generador de código ABAP — Módulo 1."""
from __future__ import annotations
from sqlalchemy.orm import Session

from app.services.ai.engine import run_agent, parse_json
from app.services.ai.agents import json_instruction

# El agente se elige según la versión SAP del contexto.
def _pick_agent(sap_version: str, dev_type: str) -> str:
    s4_types = {"cds", "amdp", "rap", "odata", "segw"}
    if (dev_type or "").lower() in s4_types:
        return "abap_s4"
    if (dev_type or "").lower() in {"webdynpro", "wda"}:
        return "webdynpro"
    if (sap_version or "").upper().startswith("S4"):
        return "abap_s4"
    return "abap_ecc"


_SCHEMA = (
    '{"object_name": "<nombre sugerido>", "language": "abap_oo|abap_classic", '
    '"code": "<código ABAP completo>", "explanation": "<explicación funcional y técnica>"}'
)


def generate_code(
    db: Session,
    *,
    description: str,
    sap_context: dict,
    project_id: int | None = None,
    user_id: int | None = None,
    agent_override: str | None = None,
):
    agent_key = agent_override or _pick_agent(
        sap_context.get("sap_version", ""), sap_context.get("dev_type", "")
    )

    ctx_lines = "\n".join(f"- {k}: {v}" for k, v in sap_context.items() if v)
    prompt = (
        "Genera el objeto de desarrollo ABAP solicitado.\n\n"
        f"# Contexto SAP\n{ctx_lines}\n\n"
        f"# Requerimiento\n{description}\n\n"
        + json_instruction(_SCHEMA)
    )

    result = run_agent(
        db, agent_key, prompt,
        operation="generate", project_id=project_id, user_id=user_id,
    )
    data = parse_json(result.text)
    return {
        "agent_key": agent_key,
        "provider": result.provider,
        "model": result.model,
        "tokens_in": result.tokens_in,
        "tokens_out": result.tokens_out,
        "latency_ms": result.latency_ms,
        "object_name": data.get("object_name") or "ZAB_OBJECT",
        "language": data.get("language") or "abap_oo",
        "code": data.get("code") or result.text,
        "explanation": data.get("explanation") or "",
    }
