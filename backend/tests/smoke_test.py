"""Smoke test end-to-end con TestClient sobre SQLite (sin Docker/Postgres).

Valida: auth+JWT, guards por rol, escritura/lectura ORM, catálogo, dashboard,
versionado de artefactos y aprobación, y que los endpoints de IA degraden a 503
limpio cuando no hay API key. NO llama a proveedores reales de IA.
"""
import os
import sys
os.environ["TESTING"] = "1"
# Permite ejecutar el test desde cualquier cwd (agrega backend/ al path)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.core.database import Base, get_db
from app.core.security import get_password_hash
import app.models  # noqa
from app.models.user import User, UserRole
from app.main import app

# BD SQLite en memoria compartida entre conexiones
engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSession = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base.metadata.create_all(engine)


def override_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_db

# Seed mínimo: admin + consultor + qa
seed = TestingSession()
seed.add_all([
    User(email="admin@x.io", password_hash=get_password_hash("pass1234"), first_name="A", last_name="D", role=UserRole.admin),
    User(email="cons@x.io", password_hash=get_password_hash("pass1234"), first_name="C", last_name="O", role=UserRole.consultant),
    User(email="ro@x.io", password_hash=get_password_hash("pass1234"), first_name="R", last_name="O", role=UserRole.client_readonly),
])
seed.commit()
seed.close()

c = TestClient(app)
PASS, FAIL = 0, 0


def check(name, cond):
    global PASS, FAIL
    if cond:
        PASS += 1; print(f"  PASS  {name}")
    else:
        FAIL += 1; print(f"  FAIL  {name}")


def token(email):
    r = c.post("/api/auth/login", json={"email": email, "password": "pass1234"})
    return r.json().get("access_token")


print("\n== Auth ==")
r = c.post("/api/auth/login", json={"email": "admin@x.io", "password": "pass1234"})
check("login admin 200", r.status_code == 200 and "access_token" in r.json())
check("login mala pass 401", c.post("/api/auth/login", json={"email": "admin@x.io", "password": "nope"}).status_code == 401)
admin_h = {"Authorization": f"Bearer {token('admin@x.io')}"}
cons_h = {"Authorization": f"Bearer {token('cons@x.io')}"}
ro_h = {"Authorization": f"Bearer {token('ro@x.io')}"}
check("/auth/me 200", c.get("/api/auth/me", headers=admin_h).status_code == 200)
check("/auth/me sin token 401", c.get("/api/auth/me").status_code == 401)

print("\n== Catálogo y salud ==")
check("/health 200", c.get("/health").status_code == 200)
cat = c.get("/api/catalog/")
check("/catalog dev_types", cat.status_code == 200 and len(cat.json()["dev_types"]) > 10)

print("\n== Roles (RBAC) ==")
check("cliente RO no crea cliente 403",
      c.post("/api/clients/", headers=ro_h, json={"name": "X"}).status_code == 403)
r = c.post("/api/clients/", headers=cons_h, json={"name": "Cliente Demo", "naming_convention": "Z*"})
check("consultor crea cliente 201", r.status_code == 201)
client_id = r.json()["id"]

print("\n== Proyectos y requerimientos ==")
r = c.post("/api/projects/", headers=cons_h, json={"name": "Proy 1", "client_id": client_id, "sap_version": "S4HANA"})
check("crea proyecto 201", r.status_code == 201)
pid = r.json()["id"]
check("lista proyectos", any(p["id"] == pid for p in c.get("/api/projects/", headers=cons_h).json()))
r = c.post("/api/projects/requirements", headers=cons_h, json={"project_id": pid, "title": "Req 1", "description": "test"})
check("crea requerimiento 201", r.status_code == 201)

print("\n== Versionado + aprobación (insert directo de artefacto) ==")
db = TestingSession()
from app.models.code_artifact import CodeArtifact
art = CodeArtifact(project_id=pid, name="ZAB_T", language="abap_oo", code="REPORT zab_t.", version=1, status="generated")
db.add(art); db.commit(); aid = art.id; db.close()
r = c.patch(f"/api/generation/artifacts/{aid}", headers=cons_h, json={"code": "REPORT zab_t.\nWRITE 'v2'."})
check("PATCH crea v2", r.status_code == 200 and r.json()["version"] == 2)
v2 = r.json()["id"]
vers = c.get(f"/api/generation/artifacts/{v2}/versions", headers=cons_h).json()
check("cadena de versiones = 2", len(vers) == 2)
check("consultor NO aprueba (403)", c.post(f"/api/generation/artifacts/{v2}/approve", headers=cons_h).status_code == 403)
r = c.post(f"/api/generation/artifacts/{v2}/approve", headers=admin_h)
check("admin aprueba 200", r.status_code == 200 and r.json()["status"] == "approved")

print("\n== Dashboard y costos ==")
check("dashboard stats", c.get("/api/dashboard/stats", headers=cons_h).status_code == 200)
check("costos requiere approver (consultor 403)", c.get("/api/costs/summary", headers=cons_h).status_code == 403)
check("costos admin 200", c.get("/api/costs/summary", headers=admin_h).status_code == 200)

print("\n== Linter ABAP estático (sin IA) ==")
from app.services import abap_lint
bad = "REPORT z.\nLOOP AT lt INTO ls.\n  SELECT * FROM bseg INTO ls2 WHERE belnr = ls-belnr.\nENDLOOP.\nDELETE FROM ztabla."
lr = abap_lint.lint(bad)
rules = {f["rule"] for f in lr["findings"]}
check("detecta SELECT * ", "ZAB001_SELECT_STAR" in rules)
check("detecta SELECT en LOOP", "ZAB002_SELECT_IN_LOOP" in rules)
check("detecta DELETE sin WHERE (critical)", "ZAB003_DELETE_NO_WHERE" in rules)
check("DELETE sin WHERE es bloqueante", abap_lint.has_blocking_issues(lr))
clean = "REPORT z.\nAUTHORITY-CHECK OBJECT 'S_X'.\nSELECT belnr FROM bkpf INTO TABLE @lt WHERE bukrs = @p_b."
check("código limpio sin críticos", not abap_lint.has_blocking_issues(abab := abap_lint.lint(clean)))

print("\n== /validate endpoint (sin IA) ==")
rv = c.post("/api/generation/validate", headers=cons_h, json={"source_code": bad})
check("/validate 200 con findings", rv.status_code == 200 and rv.json()["critical_count"] >= 1)

print("\n== Recetas (sin IA) ==")
rr = c.get("/api/recipes/", headers=cons_h)
check("recetas listadas", rr.status_code == 200 and len(rr.json()) >= 5)

print("\n== Memoria del cliente (RAG) ==")
rk = c.post("/api/knowledge/", headers=cons_h, json={
    "client_id": client_id, "kind": "z_object", "title": "Clase util ZCL_FI_TOOLS",
    "content": "Clase utilitaria ZCL_FI_TOOLS con metodo get_partidas_abiertas para sociedad y fecha."})
check("ingesta knowledge 201", rk.status_code == 201)
from app.services import client_knowledge
ses = TestingSession()
ctx_txt = client_knowledge.retrieve(ses, client_id, "necesito partidas abiertas por sociedad")
ses.close()
check("RAG recupera fragmento relevante", "ZCL_FI_TOOLS" in ctx_txt)
check("RAG vacío si query irrelevante", client_knowledge.retrieve(TestingSession(), client_id, "color azul gatos") == "")

print("\n== Catálogo ABAP moderno / Cloud / BTP ==")
cat2 = c.get("/api/catalog/").json()
check("versión BTP_ABAP en catálogo", any(v["key"] == "BTP_ABAP" for v in cat2["sap_versions"]))
check("destinos de migración", len(cat2.get("migration_targets", [])) >= 3)
check("dev_types incluye RAP/EML/service_binding",
      {"rap_managed", "eml", "service_binding"}.issubset({d["key"] for d in cat2["dev_types"]}))

print("\n== Nomenclaturas dinámicas (sin IA) ==")
from app.services import naming as naming_svc
check("apply_pattern Z{MODULE}_{NAME}", naming_svc.apply_pattern("Z{MODULE}_{NAME}", {"MODULE": "FI", "NAME": "partidas"}) == "ZFI_PARTIDAS")
check("apply_pattern ZCL_{AREA}_{NAME}", naming_svc.apply_pattern("ZCL_{AREA}_{NAME}", {"AREA": "fi", "NAME": "tools"}) == "ZCL_FI_TOOLS")
rr = c.post("/api/naming/", headers=cons_h, json={"client_id": client_id, "object_type": "table", "pattern": "Z{MODULE}_{NAME}"})
check("crea regla naming 201", rr.status_code == 201)
rules = c.get(f"/api/naming/client/{client_id}", headers=cons_h).json()
check("lista reglas naming", any(x["object_type"] == "table" for x in rules))
rp = c.post("/api/naming/preview", headers=cons_h, json={"pattern": "ZI_{NAME}", "variables": {"NAME": "factura"}})
check("preview naming", rp.json()["name"] == "ZI_FACTURA")
rules_block = naming_svc.rules_prompt(TestingSession(), client_id)
check("rules_prompt inyecta convención", "Z{MODULE}_{NAME}" in rules_block)

print("\n== IA sin API key => 503 limpio ==")
r = c.post("/api/generation/code", headers=cons_h, json={"description": "x", "sap_context": {"sap_version": "ECC"}, "save": False})
check("generate sin key 503", r.status_code == 503)
r = c.post("/api/generation/code", headers=cons_h, json={"description": "x", "sap_context": {"sap_version": "BTP_ABAP", "dev_type": "rap_managed"}, "save": False, "auto_optimize": True})
check("generate ABAP Cloud sin key 503", r.status_code == 503)
r = c.post("/api/dumps/analyze", headers=cons_h, json={"raw_dump": "DUMP", "save": False})
check("dump sin key 503", r.status_code == 503)
r = c.post("/api/generation/extract-requirement", headers=cons_h, json={"raw_text": "necesito un report"})
check("extract-requirement sin key 503", r.status_code == 503)
r = c.post("/api/migration/migrate", headers=cons_h, json={"source_code": "REPORT z.", "target": "S4HANA", "save": False})
check("migración sin key 503", r.status_code == 503)
r = c.post("/api/dev-docs/generate", headers=cons_h, json={"description": "x", "sap_context": {"sap_version": "S4HANA"}, "save": False})
check("dev-doc sin key 503", r.status_code == 503)

print(f"\n==== RESULTADO: {PASS} PASS / {FAIL} FAIL ====")
raise SystemExit(1 if FAIL else 0)
