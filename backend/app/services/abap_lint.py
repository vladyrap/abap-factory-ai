"""Linter ABAP estático — SIN IA. Rápido, determinista, robusto.

Detecta patrones peligrosos / anti-performance sin gastar un ciclo en SAP ni una
llamada a IA. Es la base de los guardrails: ciertas reglas son 'críticas' y deben
bloquear o marcar fuertemente la entrega.

Cada hallazgo: {rule, severity, line, message, suggestion}.
Severidades: critical | error | warning | info.
"""
from __future__ import annotations
import re

# Peso de cada severidad para el score 0-100
_WEIGHTS = {"critical": 35, "error": 15, "warning": 6, "info": 2}


def _strip_comment(line: str) -> str:
    """Quita comentarios ABAP: '*' en col 1 (línea completa) y '"' inline."""
    if line.lstrip().startswith("*"):
        return ""
    # comilla doble que no esté dentro de un literal '...'
    out, in_str = [], False
    i = 0
    while i < len(line):
        ch = line[i]
        if ch == "'":
            in_str = not in_str
            out.append(ch)
        elif ch == '"' and not in_str:
            break
        else:
            out.append(ch)
        i += 1
    return "".join(out)


def lint(code: str) -> dict:
    """Analiza el código y devuelve {score, findings, critical_count}."""
    raw_lines = (code or "").splitlines()
    lines = [_strip_comment(l) for l in raw_lines]
    upper = [l.upper() for l in lines]
    findings: list[dict] = []

    def add(rule, severity, line_no, message, suggestion):
        findings.append({"rule": rule, "severity": severity, "line": line_no,
                         "message": message, "suggestion": suggestion})

    has_authority = any("AUTHORITY-CHECK" in u for u in upper)
    db_access = False
    loop_depth = 0

    for idx, u in enumerate(upper, start=1):
        stripped = u.strip()
        if not stripped:
            continue

        # Profundidad de LOOP (para detectar SELECT dentro de LOOP)
        if re.match(r"^\s*LOOP\b", u):
            loop_depth += 1
        if re.match(r"^\s*ENDLOOP\b", u):
            loop_depth = max(0, loop_depth - 1)

        is_select = bool(re.search(r"\bSELECT\b", u))
        is_dbwrite = bool(re.search(r"\b(INSERT|UPDATE|MODIFY|DELETE)\b\s+\w", u))
        if is_select or is_dbwrite:
            db_access = True

        # ZAB001 — SELECT *
        if re.search(r"\bSELECT\s+\*", u):
            add("ZAB001_SELECT_STAR", "warning", idx,
                "SELECT * trae todos los campos.", "Especifica solo los campos necesarios.")

        # ZAB002 — SELECT dentro de LOOP
        if is_select and loop_depth > 0 and "ENDSELECT" not in u:
            add("ZAB002_SELECT_IN_LOOP", "error", idx,
                "SELECT dentro de LOOP: acceso a BD repetido.",
                "Saca el SELECT del LOOP (usa FOR ALL ENTRIES, JOIN o lectura previa a tabla interna).")

        # ZAB003 — DELETE FROM dbtab sin WHERE (statement de una línea)
        if re.match(r"^\s*DELETE\s+FROM\s+\w+\s*\.?\s*$", u) and "WHERE" not in u:
            add("ZAB003_DELETE_NO_WHERE", "critical", idx,
                "DELETE FROM tabla sin WHERE: borra TODA la tabla.",
                "Agrega una cláusula WHERE o confirma que es intencional.")

        # ZAB004 — UPDATE dbtab SET sin WHERE
        if re.search(r"\bUPDATE\s+\w+\s+SET\b", u) and "WHERE" not in u:
            add("ZAB004_UPDATE_NO_WHERE", "critical", idx,
                "UPDATE ... SET sin WHERE: actualiza TODA la tabla.",
                "Agrega WHERE o confirma intención.")

        # ZAB005 — SELECT SINGLE sin WHERE
        if re.search(r"\bSELECT\s+SINGLE\b", u) and "WHERE" not in u:
            add("ZAB005_SELECT_SINGLE_NO_WHERE", "warning", idx,
                "SELECT SINGLE sin WHERE: registro indeterminado.",
                "Agrega WHERE con la clave.")

        # ZAB006 — MANDT/mandante hardcodeado
        if re.search(r"\bMANDT\b\s*=\s*'\d", u) or re.search(r"\bCLIENT\s+SPECIFIED\b", u):
            add("ZAB006_HARDCODED_CLIENT", "warning", idx,
                "Mandante/cliente referenciado explícitamente.",
                "Deja que el sistema maneje el mandante automáticamente.")

        # ZAB007 — BREAK-POINT / debug dejado
        if re.search(r"\bBREAK-POINT\b", u) or re.match(r"^\s*BREAK\s+\w", u):
            add("ZAB007_DEBUG_LEFTOVER", "error", idx,
                "BREAK-POINT en el código.", "Elimina los puntos de quiebre antes de transportar.")

        # ZAB008 — MESSAGE tipo X (genera dump)
        if re.search(r"\bMESSAGE\b.*\bTYPE\s+'X'", u):
            add("ZAB008_MESSAGE_TYPE_X", "warning", idx,
                "MESSAGE TYPE 'X' provoca un short dump.",
                "Úsalo solo para errores irrecuperables; prefiere E/A con manejo.")

        # ZAB009 — TODO/FIXME
        if "TODO" in u or "FIXME" in u or "XXX" in stripped:
            add("ZAB009_TODO", "info", idx, "Marca pendiente (TODO/FIXME).", "Resuelve antes de cerrar.")

        # ZAB010 — comparación con literal sospechosa (números mágicos en WHERE)
        if re.search(r"\bWHERE\b.*=\s*'\d{3,}'", u):
            add("ZAB010_MAGIC_VALUE", "info", idx,
                "Valor literal en condición.", "Considera parametrizar o usar constante.")

    # ZAB011 — sin AUTHORITY-CHECK habiendo acceso a BD
    if db_access and not has_authority:
        add("ZAB011_NO_AUTHORITY_CHECK", "warning", 0,
            "Hay acceso a BD pero no se encontró AUTHORITY-CHECK.",
            "Agrega AUTHORITY-CHECK para datos sensibles.")

    penalty = sum(_WEIGHTS.get(f["severity"], 0) for f in findings)
    score = max(0, 100 - penalty)
    critical_count = sum(1 for f in findings if f["severity"] == "critical")
    return {"score": score, "findings": findings, "critical_count": critical_count}


def has_blocking_issues(lint_result: dict) -> bool:
    """True si hay hallazgos críticos (guardrail duro)."""
    return lint_result.get("critical_count", 0) > 0
