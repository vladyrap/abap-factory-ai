"""Generador de documento técnico: inventario de objetos + paso a paso."""
from __future__ import annotations
from sqlalchemy.orm import Session

from app.services.ai.engine import run_agent, parse_json
from app.services.ai.agents import json_instruction
from app.services import naming

_SCHEMA = (
    '{"title": "<título del desarrollo>", "summary": "<resumen técnico>", '
    '"objects": [{"name": "<nombre exacto>", "type": "<clase|tabla|estructura|CDS|report|FM|'
    'behavior|service_binding|elemento_datos|dominio|...>", "action": "crear|modificar|usar", '
    '"package": "<paquete>", "description": "<para qué sirve>", "dependencies": "<de qué depende>"}], '
    '"steps": [{"n": 1, "title": "<título del paso>", "detail": "<qué hacer>", '
    '"objects": ["<objetos involucrados>"]}], '
    '"transport_plan": "<orden de transporte y dependencias>", '
    '"rollback_plan": "<cómo revertir>"}'
)


def generate_document(
    db: Session,
    *,
    description: str,
    sap_context: dict,
    project_id: int | None = None,
    user_id: int | None = None,
    client_id: int | None = None,
):
    agent_key = "abap_cloud" if str(sap_context.get("sap_version", "")).upper() in {"S4HANA_CLOUD_PUBLIC", "BTP_ABAP"} \
        else ("abap_s4" if str(sap_context.get("sap_version", "")).upper().startswith("S4") else "abap_ecc")
    ctx_lines = "\n".join(f"- {k}: {v}" for k, v in sap_context.items() if v)
    naming_block = naming.rules_prompt(db, client_id) if client_id else ""

    prompt = (
        "Elabora el documento técnico de este desarrollo SAP. Lista CADA objeto que se tocará o creará "
        "con su NOMBRE EXACTO (respetando la convención de nombres del cliente si se entrega), su tipo, "
        "la acción (crear/modificar/usar), su paquete y dependencias. Luego entrega una guía de "
        "construcción paso a paso, el plan de transporte y el plan de rollback.\n\n"
        f"# Contexto SAP\n{ctx_lines}\n\n{naming_block}"
        f"# Requerimiento\n{description}\n\n"
        + json_instruction(_SCHEMA)
    )
    result = run_agent(db, agent_key, prompt, operation="dev_doc",
                       project_id=project_id, user_id=user_id)
    data = parse_json(result.text)
    data["_meta"] = {"provider": result.provider, "model": result.model}
    return data
