"""Generación auto-optimizada (self-healing) — el consultor recibe código que YA pasó calidad.

Flujo: generar → lint estático (sin IA) → inspeccionar (IA) → si score bajo, refactorizar
con feedback → repetir hasta alcanzar el objetivo o agotar iteraciones.
"""
from __future__ import annotations
import logging
from sqlalchemy.orm import Session

from app.services import abap_lint
from app.services.ai import generator, inspector
from app.services.ai.engine import run_agent, parse_json
from app.services.ai.agents import json_instruction

logger = logging.getLogger(__name__)

_REFACTOR_SCHEMA = '{"code": "<código ABAP corregido completo>", "notes": "<cambios aplicados>"}'


def _refactor_with_feedback(db, code, findings, project_id, user_id):
    """Pide al agente Inspector que corrija el código según hallazgos concretos."""
    issues = "\n".join(
        f"- [{f.get('severity')}] {f.get('rule', '')} (línea {f.get('line')}): {f.get('message')} → {f.get('suggestion')}"
        for f in findings
    )
    prompt = (
        "Corrige el siguiente código ABAP resolviendo TODOS los hallazgos listados, sin cambiar "
        "su comportamiento funcional y aplicando Clean ABAP.\n\n"
        f"# Hallazgos a resolver\n{issues}\n\n"
        f"# Código\n```abap\n{code[:12000]}\n```\n\n"
        + json_instruction(_REFACTOR_SCHEMA)
    )
    result = run_agent(db, "inspector", prompt, operation="editor_refactor",
                       project_id=project_id, user_id=user_id)
    data = parse_json(result.text)
    return data.get("code") or code


def generate_optimized(
    db: Session,
    *,
    description: str,
    sap_context: dict,
    project_id: int | None = None,
    user_id: int | None = None,
    client_id: int | None = None,
    target_score: int = 80,
    max_iters: int = 2,
):
    """Genera y auto-optimiza hasta alcanzar target_score (o agotar max_iters)."""
    gen = generator.generate_code(
        db, description=description, sap_context=sap_context,
        project_id=project_id, user_id=user_id, client_id=client_id,
    )
    code = gen["code"]
    timeline = []

    def evaluate(stage_code):
        lint = abap_lint.lint(stage_code)
        insp = inspector.inspect_code(
            db, source_code=stage_code, sap_context=sap_context,
            project_id=project_id, user_id=user_id,
        )
        # Score combinado: el menor entre lint estático e inspector IA (conservador)
        combined = min(lint["score"], insp.get("score", 0))
        return lint, insp, combined

    lint, insp, score = evaluate(code)
    timeline.append({"iter": 0, "stage": "generado", "lint_score": lint["score"],
                     "inspector_score": insp.get("score"), "combined": score,
                     "critical": lint["critical_count"]})

    it = 0
    while score < target_score and it < max_iters:
        it += 1
        findings = lint["findings"] + insp.get("findings", [])
        code = _refactor_with_feedback(db, code, findings, project_id, user_id)
        lint, insp, score = evaluate(code)
        timeline.append({"iter": it, "stage": "refactorizado", "lint_score": lint["score"],
                         "inspector_score": insp.get("score"), "combined": score,
                         "critical": lint["critical_count"]})

    return {
        "agent_key": gen["agent_key"], "provider": gen["provider"], "model": gen["model"],
        "object_name": gen["object_name"], "language": gen["language"],
        "code": code, "explanation": gen["explanation"],
        "confidence_notes": gen["confidence_notes"], "used_knowledge": gen["used_knowledge"],
        "final_score": score, "passed": score >= target_score,
        "lint": lint, "inspection": insp, "timeline": timeline,
        "iterations": it,
    }
