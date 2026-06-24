"""Datos demo para ABAP Factory AI. Ejecutar: python seed.py"""
from app.core.database import SessionLocal, Base, engine
from app.core.security import get_password_hash
import app.models  # noqa
from app.models.user import User, UserRole
from app.models.client import Client
from app.models.project import Project

Base.metadata.create_all(bind=engine)
db = SessionLocal()


def upsert_user(email, first, last, role):
    u = db.query(User).filter(User.email == email).first()
    if not u:
        u = User(email=email, password_hash=get_password_hash("demo1234"),
                 first_name=first, last_name=last, role=role)
        db.add(u)
    return u


print("Creando usuarios demo (password: demo1234)...")
admin = upsert_user("admin@abapfactory.ai", "Admin", "Sistema", UserRole.admin)
upsert_user("lider@abapfactory.ai", "Laura", "Líder", UserRole.tech_lead)
upsert_user("consultor@abapfactory.ai", "Carlos", "Consultor", UserRole.consultant)
upsert_user("qa@abapfactory.ai", "Quita", "Tester", UserRole.qa)
upsert_user("cliente@abapfactory.ai", "Clara", "Cliente", UserRole.client_readonly)
db.commit()

print("Creando cliente y proyecto demo...")
if not db.query(Client).first():
    client = Client(
        name="Industrias Demo S.A.", industry="Manufactura",
        contact_name="Pedro Pérez", contact_email="pedro@demo.cl",
        naming_convention="Prefijo Z, formato ZAB_<modulo>_<objeto>",
        coding_standards="Clean ABAP. Prohibido SELECT *. AUTHORITY-CHECK obligatorio.",
        restrictions="No modificar objetos estándar SAP.",
    )
    db.add(client)
    db.flush()
    db.add(Project(
        client_id=client.id, owner_user_id=admin.id, name="Migración Reportes FI",
        code="MIG-FI-2026", description="Migración de reports FI de ECC a S/4HANA",
        sap_version="S4HANA", modules=["FI", "CO"], sap_package="ZAB_FI",
        transport_request="DEVK900123", mandante="100", environment="DEV",
    ))
    db.commit()

print("Listo. Usuarios: admin@abapfactory.ai / demo1234")
db.close()
