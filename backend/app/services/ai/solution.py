"""Orquestador 'Requerimiento → Solución'.

Lee un requerimiento funcional en texto libre, CLASIFICA qué se necesita (programa
nuevo, fix, corrección de bug, mejora, migración o fix de dump) y EJECUTA el camino
correcto reutilizando los servicios especializados. Devuelve un resultado unificado.
"""
from __future__ import annotations
import logging
from sqlalchemy.orm import Session

from app.services.ai.engine import run_agent, parse_json
from app.services.ai.agents import json_instruction
from app.services.ai import generator, dump_solver, migrator
from app.services import abap_lint, naming

logger = logging.getLogger(__name__)

SOLUTION_TYPES = ("nuevo_desarrollo", "correccion_bug", "mejora_enhancement",
                  "fix_dump", "migracion", "ajuste")

_CLASSIFY_SCHEMA = (
    '{"solution_type": "nuevo_desarrollo|correccion_bug|mejora_enhancement|fix_dump|migracion|ajuste", '
    '"title": "<título corto>", "description": "<requerimiento técnico claro y accionable>", '
    '"sap_version": "ECC|S4HANA|S4HANA_CLOUD_PRIVATE|S4HANA_CLOUD_PUBLIC|BTP_ABAP", '
    '"module": "<FI|CO|MM|SD|PP|QM|PM|HR|Basis|Integracion>", '
    '"dev_type": "<report|alv|salv|cds|rap|bapi|badi|idoc|enhancement|...>", '
    '"complexity": "baja|media|alta|critica", "target_object": "<objeto a tocar si aplica>", '
    '"needs_existing_code": true, "reasoning": "<por qué ese tipo>", "steps": ["<paso del plan>"]}'
)

_FIX_SCHEMA = (
    '{"code": "<código resultante completo>", "explanation": "<qué se hizo y por qué>", '
    '"changes": [{"before": "<fragmento>", "after": "<fragmento>", "reason": "<motivo>"}], '
    '"confidence_notes": [{"item": "<objeto a verificar>", "reason": "...", "confidence": "alta|media|baja"}]}'
)


def classify(db: Session, text: str, project_id=None, user_id=None) -> dict:
    prompt = (
        "Eres un líder técnico SAP. Lee el siguiente requerimiento funcional y determina QUÉ tipo de "
        "solución corresponde y su contexto. Si describe un error/dump, es 'fix_dump'; si pide cambiar "
        "código existente, 'correccion_bug' o 'mejora_enhancement'; si pide migrar a S/4, 'migracion'; "
        "si es algo nuevo, 'nuevo_desarrollo'.\n\n"
        f"# Requerimiento funcional\n{text[:12000]}\n\n"
        + json_instruction(_CLASSIFY_SCHEMA)
    )
    result = run_agent(db, "abap_ecc", prompt, operation="classify",
                       project_id=project_id, user_id=user_id)
    data = parse_json(result.text)
    if data.get("solution_type") not in SOLUTION_TYPES:
        data["solution_type"] = "nuevo_desarrollo"
    return data


def _fix_existing(db, *, instruction, existing_code, sap_context, agent_key, project_id, user_id):
    naming_block = naming.rules_prompt(db, sap_context.get("_client_id")) if sap_context.get("_client_id") else ""
    ctx_lines = "\n".join(f"- {k}: {v}" for k, v in sap_context.items() if v and not k.startswith("_"))
    prompt = (
        "Aplica el siguiente requerimiento de cambio/corrección al código ABAP existente, manteniendo "
        "el comportamiento no afectado y aplicando Clean ABAP. Detalla cada cambio.\n\n"
        f"# Contexto SAP\n{ctx_lines}\n\n{naming_block}"
        f"# Requerimiento\n{instruction}\n\n"
        f"# Código existente\n```abap\n{existing_code[:12000]}\n```\n\n"
        + json_instruction(_FIX_SCHEMA)
    )
    result = run_agent(db, agent_key, prompt, operation="fix",
                       project_id=project_id, user_id=user_id)
    data = parse_json(result.text)
    data["_meta"] = {"provider": result.provider, "model": result.model}
    return data


def build(
    db: Session,
    *,
    requirement_text: str,
    existing_code: str | None = None,
    sap_context_override: dict | None = None,
    project_id: int | None = None,
    user_id: int | None = None,
    client_id: int | None = None,
):
    """Pipeline completo: clasifica y ejecuta el camino adecuado."""
    cls = classify(db, requirement_text, project_id, user_id)

    # Contexto SAP: lo inferido por la clasificación + override del usuario (gana el override).
    ctx = {
        "sap_version": cls.get("sap_version") or "S4HANA",
        "module": cls.get("module"),
        "dev_type": cls.get("dev_type"),
        "complexity": cls.get("complexity") or "media",
    }
    if sap_context_override:
        ctx.update({k: v for k, v in sap_context_override.items() if v})

    stype = cls["solution_type"]
    desc = cls.get("description") or requirement_text
    out = {"solution_type": stype, "classification": cls, "sap_context": ctx}

    # ─── Camino 1: fix de dump ──────────────────────────────────────────────
    if stype == "fix_dump" and existing_code:
        dump = dump_solver.analyze_dump(db, raw_dump=existing_code, project_id=project_id,
                                        user_id=user_id, sap_context=ctx)
        out.update({"kind": "dump", "code": dump.get("fixed_code") or "",
                    "explanation": dump.get("root_cause"), "dump": dump,
                    "object_name": dump.get("program") or "FIX", "language": "abap_oo",
                    "confidence_notes": []})
        return out

    # ─── Camino 2: migración con código existente ───────────────────────────
    if stype == "migracion" and existing_code:
        target = ctx.get("sap_version") if ctx.get("sap_version", "").upper().startswith(("S4", "BTP")) else "S4HANA"
        mig = migrator.migrate_code(db, source_code=existing_code, target=target,
                                    project_id=project_id, user_id=user_id)
        out.update({"kind": "migration", "code": mig.get("migrated_code") or "",
                    "explanation": mig.get("notes"), "changes": mig.get("changes", []),
                    "migration": mig, "object_name": "MIGRADO", "language": "abap_oo",
                    "confidence_notes": []})
        return out

    # ─── Camino 3: corrección/mejora/ajuste sobre código existente ──────────
    if stype in ("correccion_bug", "mejora_enhancement", "ajuste") and existing_code:
        agent_key = generator._pick_agent(ctx.get("sap_version", ""), ctx.get("dev_type", ""))
        ctx2 = dict(ctx); ctx2["_client_id"] = client_id
        fix = _fix_existing(db, instruction=desc, existing_code=existing_code, sap_context=ctx2,
                            agent_key=agent_key, project_id=project_id, user_id=user_id)
        code = fix.get("code") or existing_code
        out.update({"kind": "fix", "code": code, "explanation": fix.get("explanation"),
                    "changes": fix.get("changes", []), "confidence_notes": fix.get("confidence_notes", []),
                    "object_name": cls.get("target_object") or "AJUSTE", "language": "abap_oo",
                    "lint": abap_lint.lint(code)})
        return out

    # ─── Camino 4 (default): desarrollo nuevo ───────────────────────────────
    gen = generator.generate_code(db, description=desc, sap_context=ctx,
                                  project_id=project_id, user_id=user_id, client_id=client_id)
    out.update({"kind": "new", "code": gen["code"], "explanation": gen["explanation"],
                "object_name": gen["object_name"], "language": gen["language"],
                "confidence_notes": gen["confidence_notes"], "agent_key": gen["agent_key"],
                "lint": abap_lint.lint(gen["code"])})
    return out
