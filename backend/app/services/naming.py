"""Motor de nomenclaturas dinámicas — SIN IA.

Sustituye marcadores {VAR} en un patrón por valores, en mayúsculas, respetando el
estilo SAP. Cada empresa define sus propios patrones por tipo de objeto.
"""
from __future__ import annotations
import re
from sqlalchemy.orm import Session
from app.models.naming_rule import NamingRule


def apply_pattern(pattern: str, variables: dict) -> str:
    """ "Z{MODULE}_{NAME}" + {MODULE: FI, NAME: partidas} -> "ZFI_PARTIDAS" """
    def repl(m):
        key = m.group(1)
        val = str(variables.get(key, variables.get(key.lower(), ""))).strip()
        return re.sub(r"[^A-Za-z0-9]", "_", val)
    name = re.sub(r"\{(\w+)\}", repl, pattern or "")
    name = re.sub(r"_{2,}", "_", name).strip("_")
    return name.upper()


def placeholders(pattern: str) -> list[str]:
    return re.findall(r"\{(\w+)\}", pattern or "")


def get_rules(db: Session, client_id: int | None) -> list[NamingRule]:
    if not client_id:
        return []
    return (
        db.query(NamingRule)
        .filter(NamingRule.client_id == client_id)
        .order_by(NamingRule.object_type)
        .all()
    )


def rules_prompt(db: Session, client_id: int | None) -> str:
    """Bloque para inyectar en el prompt del generador: convenciones del cliente."""
    rules = get_rules(db, client_id)
    if not rules:
        return ""
    lines = [f"- {r.object_type}: patrón `{r.pattern}`" + (f" (ej: {r.example})" if r.example else "")
             for r in rules]
    return (
        "# Convención de nombres del cliente (OBLIGATORIA — aplícala a cada objeto que crees)\n"
        + "\n".join(lines) + "\n\n"
    )
