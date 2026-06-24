"""Analizador de Dumps ST22 — Módulo 5."""
from __future__ import annotations
from sqlalchemy.orm import Session

from app.services.ai.engine import run_agent, parse_json
from app.services.ai.agents import json_instruction

_SCHEMA = (
    '{"dump_type": "<categoría ST22>", "severity": "baja|media|alta|critica", '
    '"program": "...", "include": "...", "line": "...", "sap_object": "...", '
    '"root_cause": "<causa raíz explicada>", "solution": "<solución técnica>", '
    '"fixed_code": "<fragmento ABAP corregido>", '
    '"checklist": ["<paso de revisión>"], "suggested_tests": ["<prueba sugerida>"]}'
)


def analyze_dump(
    db: Session,
    *,
    raw_dump: str,
    project_id: int | None = None,
    user_id: int | None = None,
    sap_context: dict | None = None,
):
    ctx = ""
    if sap_context:
        ctx = "# Contexto SAP\n" + "\n".join(f"- {k}: {v}" for k, v in sap_context.items() if v) + "\n\n"
    prompt = (
        "Analiza el siguiente dump de SAP (ST22). Identifica tipo, causa raíz, ubicación "
        "(programa/include/línea/objeto), propón solución y código corregido, y clasifica la "
        "severidad.\n\n"
        f"{ctx}# Dump\n```\n{raw_dump[:12000]}\n```\n\n"
        + json_instruction(_SCHEMA)
    )
    result = run_agent(db, "dump_solver", prompt, operation="dump", project_id=project_id, user_id=user_id)
    data = parse_json(result.text)
    data["_meta"] = {"provider": result.provider, "model": result.model}
    return data
