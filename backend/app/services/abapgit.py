"""Exportación a formato abapGit — SIN IA.

Genera un ZIP con la estructura que abapGit espera (carpeta src/ + .abapgit.xml),
listo para hacer `pull`/`push` a un repositorio abapGit (online o offline) y de ahí
transportar a SAP. La "integración" real con el sistema es vía git: el equipo importa
este ZIP en su repo abapGit y lo activa/transporta desde ADT o SE80.
"""
from __future__ import annotations
import io
import json
import re
import zipfile

# Mapeo dev_type/lenguaje -> sufijo de objeto abapGit
_SUFFIX = {
    "class": "clas", "abap_cloud_class": "clas",
    "interface": "intf",
    "report": "prog", "report_oo": "prog", "module_pool": "prog", "alv": "prog",
    "salv": "prog", "job": "prog", "include": "prog",
    "function_group": "fugr", "function_module": "fugr", "rfc": "fugr", "bapi": "fugr",
    "cds": "ddls", "cds_analytical": "ddls", "cds_transactional": "ddls",
    "behavior_def": "bdef", "behavior": "bdef",
    "amdp": "clas",
}
_EXT = {"ddls": "asddls", "bdef": "asbdef"}


def _safe(name: str) -> str:
    return re.sub(r"[^a-z0-9_]", "_", (name or "zobject").lower()).strip("_") or "zobject"


def _suffix(artifact) -> str:
    dt = (artifact.dev_type or "").lower()
    if dt in _SUFFIX:
        return _SUFFIX[dt]
    if (artifact.language or "") == "abap_oo":
        return "clas"
    return "prog"


def _filename(artifact) -> str:
    sfx = _suffix(artifact)
    ext = _EXT.get(sfx, "abap")
    return f"{_safe(artifact.name)}.{sfx}.{ext}"


_ABAPGIT_XML = """<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_SERIALIZER" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <DATA>
    <MASTER_LANGUAGE>S</MASTER_LANGUAGE>
    <STARTING_FOLDER>/src/</STARTING_FOLDER>
    <FOLDER_LOGIC>PREFIX</FOLDER_LOGIC>
   </DATA>
  </asx:values>
 </asx:abap>
</abapGit>
"""


def build_zip(project: dict, artifacts: list) -> bytes:
    """Construye un ZIP abapGit con todos los artefactos de código del proyecto."""
    buf = io.BytesIO()
    manifest = {"project": project.get("name"), "package": project.get("sap_package"),
                "transport_request": project.get("transport_request"), "objects": []}

    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr(".abapgit.xml", _ABAPGIT_XML)
        seen = {}
        for a in artifacts:
            fname = _filename(a)
            # evita choques de nombre (versiones)
            if fname in seen:
                seen[fname] += 1
                base, _, rest = fname.partition(".")
                fname = f"{base}_{seen[fname]}.{rest}"
            else:
                seen[fname] = 0
            z.writestr(f"src/{fname}", a.code or "")
            manifest["objects"].append({
                "name": a.name, "type": a.dev_type, "file": f"src/{fname}",
                "version": a.version, "status": a.status,
            })
        z.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
        z.writestr("README.md", (
            f"# {project.get('name')} — paquete abapGit\n\n"
            f"Paquete SAP: {project.get('sap_package') or '(define en SE80/ADT)'}\n"
            f"Orden de transporte: {project.get('transport_request') or '(asigna al activar)'}\n\n"
            "## Cómo importar\n"
            "1. Crea un repositorio abapGit (online u offline) apuntando al paquete destino.\n"
            "2. Descomprime este ZIP en el repo (carpeta `src/`) o usa 'Import package' (offline).\n"
            "3. Haz **pull** desde abapGit en tu sistema (DEV) y activa los objetos.\n"
            "4. Asígnalos a la orden de transporte indicada y transporta a QAS/PRD.\n"
        ))
    return buf.getvalue()
