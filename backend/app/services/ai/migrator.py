"""Migración de código ABAP de ECC a S/4HANA / ABAP Cloud."""
from __future__ import annotations
from sqlalchemy.orm import Session

from app.services.ai.engine import run_agent, parse_json
from app.services.ai.agents import json_instruction

_SCHEMA = (
    '{"migrated_code": "<código migrado completo>", '
    '"changes": [{"area": "<SQL|tabla|API|sintaxis|...>", "before": "<fragmento original>", '
    '"after": "<fragmento migrado>", "reason": "<por qué cambia>"}], '
    '"simplification_items": [{"item": "<SI-Note/área>", "table": "<tabla afectada>", "note": "<impacto>"}], '
    '"compatibility": "ok|parcial|manual", "notes": "<resumen técnico>", '
    '"manual_steps": ["<paso que requiere intervención manual>"]}'
)

_TARGET_LABEL = {
    "S4HANA": "SAP S/4HANA on-premise (ABAP estándar)",
    "S4HANA_CLOUD_PUBLIC": "S/4HANA Cloud Public (ABAP Cloud, solo APIs liberadas)",
    "BTP_ABAP": "SAP BTP ABAP Environment / Steampunk (ABAP Cloud, RAP)",
}


def migrate_code(
    db: Session,
    *,
    source_code: str,
    target: str = "S4HANA",
    project_id: int | None = None,
    user_id: int | None = None,
):
    # ABAP Cloud/BTP => agente cloud; on-prem S/4 => agente S/4
    agent_key = "abap_cloud" if target in {"S4HANA_CLOUD_PUBLIC", "BTP_ABAP"} else "abap_s4"
    target_desc = _TARGET_LABEL.get(target, target)

    prompt = (
        f"Migra el siguiente código ABAP de SAP ECC a {target_desc}. Resuelve simplification items "
        "(tablas/campos obsoletos como BSEG, VBUK, MARC extendidos), reemplaza accesos no compatibles, "
        "moderniza la sintaxis (inline declarations, table expressions, Open SQL nuevo) y, si el destino "
        "es ABAP Cloud, usa únicamente APIs liberadas y elimina sentencias no permitidas. Detalla cada "
        "cambio en 'changes' y lo que requiera intervención manual en 'manual_steps'.\n\n"
        f"# Código ECC original\n```abap\n{source_code[:12000]}\n```\n\n"
        + json_instruction(_SCHEMA)
    )
    result = run_agent(db, agent_key, prompt, operation="migrate",
                       project_id=project_id, user_id=user_id)
    data = parse_json(result.text)
    data["_meta"] = {"provider": result.provider, "model": result.model}
    return data
