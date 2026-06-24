"""Code Inspector / ATC Advisor — Módulo 6."""
from __future__ import annotations
from sqlalchemy.orm import Session

from app.services.ai.engine import run_agent, parse_json
from app.services.ai.agents import json_instruction

_SCHEMA = (
    '{"score": <0-100>, "s4hana_compatible": "si|parcial|no", '
    '"findings": [{"rule": "...", "severity": "info|warning|error", "line": "<n>", '
    '"message": "...", "suggestion": "..."}], '
    '"rules_violated": ["..."], "recommendation": "<recomendación profesional>", '
    '"corrected_code": "<código corregido completo>"}'
)


def inspect_code(
    db: Session,
    *,
    source_code: str,
    sap_context: dict | None = None,
    project_id: int | None = None,
    user_id: int | None = None,
):
    ctx = ""
    if sap_context:
        ctx = "# Contexto SAP\n" + "\n".join(f"- {k}: {v}" for k, v in sap_context.items() if v) + "\n\n"
    prompt = (
        "Realiza una revisión de calidad estilo SAP Code Inspector / ATC sobre el siguiente código "
        "ABAP. Detecta SELECT *, SELECT dentro de LOOP, falta de AUTHORITY-CHECK, hardcoding, código "
        "muerto, variables sin uso, SQL ineficiente, dumps potenciales y compatibilidad S/4HANA. "
        "Asigna un score técnico 0-100.\n\n"
        f"{ctx}# Código\n```abap\n{source_code[:12000]}\n```\n\n"
        + json_instruction(_SCHEMA)
    )
    result = run_agent(db, "inspector", prompt, operation="inspect", project_id=project_id, user_id=user_id)
    data = parse_json(result.text)
    data["_meta"] = {"provider": result.provider, "model": result.model}
    return data
