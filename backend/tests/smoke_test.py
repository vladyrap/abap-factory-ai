"""Smoke test end-to-end con TestClient sobre SQLite (sin Docker/Postgres).

Valida: auth+JWT, guards por rol, escritura/lectura ORM, catálogo, dashboard,
versionado de artefactos y aprobación, y que los endpoints de IA degraden a 503
limpio cuando no hay API key. NO llama a proveedores reales de IA.
"""
import os
os.environ["TESTING"] = "1"

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

print("\n== IA sin API key => 503 limpio ==")
r = c.post("/api/generation/code", headers=cons_h, json={"description": "x", "sap_context": {"sap_version": "ECC"}, "save": False})
check("generate sin key 503", r.status_code == 503)
r = c.post("/api/dumps/analyze", headers=cons_h, json={"raw_dump": "DUMP", "save": False})
check("dump sin key 503", r.status_code == 503)

print(f"\n==== RESULTADO: {PASS} PASS / {FAIL} FAIL ====")
raise SystemExit(1 if FAIL else 0)
