"""Generador de pruebas ABAP Unit (Módulo 7) y protocolos de prueba (Módulo 8)."""
from __future__ import annotations
from sqlalchemy.orm import Session

from app.services.ai.engine import run_agent, parse_json
from app.services.ai.agents import json_instruction

_UNIT_SCHEMA = (
    '{"test_code": "<clase de test local ABAP Unit completa>", '
    '"cases": [{"name": "...", "type": "positivo|negativo|borde|excepcion", '
    '"given": "...", "when": "...", "then": "..."}], '
    '"mocks": ["..."], "expected_coverage": "<%>", "test_data": ["..."], '
    '"execution_protocol": "<cómo ejecutar en SE80/ADT>"}'
)

_PROTOCOL_SCHEMA = (
    '{"cases": [{"case_id": "TC-001", "name": "...", "preconditions": "...", '
    '"input_data": "...", "steps": "...", "expected_result": "...", '
    '"actual_result": "", "status": "pendiente", "evidence_required": "...", '
    '"observations": ""}]}'
)


def generate_unit_tests(
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
        "Genera una clase de pruebas ABAP Unit para el código siguiente. Usa FOR TESTING, métodos "
        "GIVEN/WHEN/THEN, test doubles/mocks cuando aplique, y cubre casos positivos, negativos, "
        "borde y validación de excepciones.\n\n"
        f"{ctx}# Código bajo prueba\n```abap\n{source_code[:12000]}\n```\n\n"
        + json_instruction(_UNIT_SCHEMA)
    )
    result = run_agent(db, "qa_abap", prompt, operation="unit_test", project_id=project_id, user_id=user_id)
    data = parse_json(result.text)
    data["_meta"] = {"provider": result.provider, "model": result.model}
    return data


def generate_protocol(
    db: Session,
    *,
    description: str,
    protocol_type: str = "funcional",
    sap_context: dict | None = None,
    project_id: int | None = None,
    user_id: int | None = None,
):
    ctx = ""
    if sap_context:
        ctx = "# Contexto SAP\n" + "\n".join(f"- {k}: {v}" for k, v in sap_context.items() if v) + "\n\n"
    prompt = (
        f"Elabora un protocolo de prueba de tipo '{protocol_type}' con casos de prueba detallados "
        "para el siguiente desarrollo.\n\n"
        f"{ctx}# Desarrollo / requerimiento\n{description}\n\n"
        + json_instruction(_PROTOCOL_SCHEMA)
    )
    result = run_agent(db, "qa_abap", prompt, operation="protocol", project_id=project_id, user_id=user_id)
    data = parse_json(result.text)
    data["_meta"] = {"provider": result.provider, "model": result.model}
    return data
