"""Catálogo de permisos granulares (bajo nivel) y RBAC dinámico.

Los roles se definen en BD (tabla roles) como conjuntos de estas claves. El permiso
especial "*" otorga todo (superusuario). Para usuarios sin rol dinámico asignado se
usa el mapeo de compatibilidad por rol legado (LEGACY_ROLE_PERMS).
"""
from __future__ import annotations

# (key, label, group) — agrupados para la UI
PERMISSIONS: list[dict] = [
    # Código
    {"key": "code.generate", "label": "Generar código", "group": "Código"},
    {"key": "code.edit", "label": "Editar código", "group": "Código"},
    {"key": "code.refine", "label": "Refinar / versionar", "group": "Código"},
    {"key": "code.approve", "label": "Aprobar código", "group": "Código"},
    {"key": "code.read", "label": "Ver código", "group": "Código"},
    # Módulos IA
    {"key": "solution.build", "label": "Requerimiento → Solución", "group": "Módulos IA"},
    {"key": "spec.generate", "label": "Especificación técnica", "group": "Módulos IA"},
    {"key": "dump.analyze", "label": "Analizar dumps", "group": "Módulos IA"},
    {"key": "inspect.run", "label": "Code Inspector", "group": "Módulos IA"},
    {"key": "tests.generate", "label": "Generar pruebas", "group": "Módulos IA"},
    {"key": "protocol.generate", "label": "Protocolos de prueba", "group": "Módulos IA"},
    {"key": "migration.run", "label": "Migración ECC→S/4", "group": "Módulos IA"},
    {"key": "devdoc.generate", "label": "Documento técnico", "group": "Módulos IA"},
    {"key": "editor.run", "label": "Editor inteligente", "group": "Módulos IA"},
    # Configuración de dominio
    {"key": "project.manage", "label": "Gestionar proyectos", "group": "Gestión"},
    {"key": "client.manage", "label": "Gestionar clientes", "group": "Gestión"},
    {"key": "naming.manage", "label": "Nomenclaturas", "group": "Gestión"},
    {"key": "knowledge.manage", "label": "Memoria del cliente", "group": "Gestión"},
    {"key": "connections.manage", "label": "Conexión SAP / abapGit", "group": "Gestión"},
    # Operación
    {"key": "jobs.run", "label": "Procesos asíncronos", "group": "Operación"},
    {"key": "export.run", "label": "Exportar / descargar", "group": "Operación"},
    {"key": "costs.view", "label": "Ver costos IA", "group": "Operación"},
    # Administración
    {"key": "users.manage", "label": "Administrar usuarios", "group": "Administración"},
    {"key": "roles.manage", "label": "Administrar roles", "group": "Administración"},
    {"key": "agents.manage", "label": "Configurar agentes IA", "group": "Administración"},
    {"key": "audit.view", "label": "Ver auditoría", "group": "Administración"},
]

ALL_KEYS = [p["key"] for p in PERMISSIONS]

# Conjuntos de compatibilidad para los roles legados (usuarios sin role_id).
_BUILDER = [
    "code.generate", "code.edit", "code.refine", "code.read", "solution.build",
    "spec.generate", "dump.analyze", "inspect.run", "tests.generate", "protocol.generate",
    "migration.run", "devdoc.generate", "editor.run", "project.manage", "client.manage",
    "naming.manage", "knowledge.manage", "connections.manage", "jobs.run", "export.run",
]

LEGACY_ROLE_PERMS: dict[str, list[str]] = {
    "admin": ["*"],
    "tech_lead": _BUILDER + ["code.approve", "costs.view", "audit.view"],
    "consultant": list(_BUILDER),
    "qa": ["tests.generate", "protocol.generate", "dump.analyze", "inspect.run", "export.run", "code.read"],
    "client_readonly": ["export.run", "code.read"],
}


def has_perm(perms: set[str], key: str) -> bool:
    return "*" in perms or key in perms
