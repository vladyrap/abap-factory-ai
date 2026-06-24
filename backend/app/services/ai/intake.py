"""Ingesta de intención — extrae un requerimiento estructurado desde texto libre.

El consultor pega el correo / spec funcional / acta y el sistema deduce los campos
del selector SAP. No tiene que redactar un prompt estructurado.
"""
from __future__ import annotations
from sqlalchemy.orm import Session

from app.services.ai.engine import run_agent, parse_json
from app.services.ai.agents import json_instruction

_SCHEMA = (
    '{"title": "<título corto>", "description": "<requerimiento técnico claro y accionable>", '
    '"sap_version": "ECC|S4HANA|S4HANA_CLOUD_PRIVATE|S4HANA_CLOUD_PUBLIC", '
    '"module": "<FI|CO|MM|SD|PP|QM|PM|HR|Basis|Integracion>", '
    '"dev_type": "<report|alv|salv|cds|amdp|rap|bapi|badi|idoc|odata|...>", '
    '"complexity": "baja|media|alta|critica", '
    '"objects_hint": ["<tablas/objetos estándar mencionados>"]}'
)


def extract_requirement(
    db: Session,
    *,
    raw_text: str,
    project_id: int | None = None,
    user_id: int | None = None,
):
    prompt = (
        "Lee el siguiente texto (correo, especificación funcional o acta) y extrae un requerimiento "
        "de desarrollo SAP estructurado. Si un dato no aparece, infiere el más probable.\n\n"
        f"# Texto\n{raw_text[:12000]}\n\n"
        + json_instruction(_SCHEMA)
    )
    result = run_agent(db, "abap_ecc", prompt, operation="intake",
                       project_id=project_id, user_id=user_id)
    data = parse_json(result.text)
    data["_meta"] = {"provider": result.provider, "model": result.model}
    return data
