"""Editor ABAP inteligente — Módulo 4.

Operaciones: explicar línea por línea, refactorizar, convertir procedural→OO,
convertir ECC→S/4HANA, limpiar código legacy.
"""
from __future__ import annotations
from sqlalchemy.orm import Session

from app.services.ai.engine import run_agent, parse_json
from app.services.ai.agents import json_instruction

_EXPLAIN_SCHEMA = '{"explanation": "<explicación general>", "lines": [{"line": "<n>", "text": "<qué hace>"}]}'
_TRANSFORM_SCHEMA = '{"code": "<código resultante>", "notes": "<cambios aplicados>"}'

# operación -> (agente, instrucción, schema)
_OPS = {
    "explain": (
        "abap_ecc",
        "Explica el siguiente código ABAP de forma clara, primero en general y luego línea por línea.",
        _EXPLAIN_SCHEMA,
    ),
    "refactor": (
        "inspector",
        "Refactoriza el siguiente código aplicando Clean ABAP, sin cambiar su comportamiento.",
        _TRANSFORM_SCHEMA,
    ),
    "to_oo": (
        "abap_ecc",
        "Convierte el siguiente código ABAP procedural a ABAP Orientado a Objetos manteniendo la funcionalidad.",
        _TRANSFORM_SCHEMA,
    ),
    "ecc_to_s4": (
        "abap_s4",
        "Convierte/adapta el siguiente código de SAP ECC a S/4HANA, resolviendo simplification items y "
        "tablas/campos obsoletos. Indica los cambios en 'notes'.",
        _TRANSFORM_SCHEMA,
    ),
    "cleanup": (
        "inspector",
        "Limpia este código legacy: elimina código muerto, variables sin uso, SELECT *, y SELECT dentro "
        "de LOOP; mejora la performance del Open SQL.",
        _TRANSFORM_SCHEMA,
    ),
}


def run_editor_op(
    db: Session,
    *,
    operation: str,
    source_code: str,
    project_id: int | None = None,
    user_id: int | None = None,
):
    agent_key, instruction, schema = _OPS.get(operation, _OPS["explain"])
    prompt = (
        f"{instruction}\n\n# Código\n```abap\n{source_code[:12000]}\n```\n\n"
        + json_instruction(schema)
    )
    result = run_agent(db, agent_key, prompt, operation=f"editor_{operation}",
                       project_id=project_id, user_id=user_id)
    data = parse_json(result.text)
    data["_meta"] = {"provider": result.provider, "model": result.model, "operation": operation}
    return data
