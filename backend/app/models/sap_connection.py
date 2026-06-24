from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from app.core.database import Base


class SapConnection(Base):
    """Config de destino abapGit/ADT por proyecto (metadatos, NO credenciales).

    Las credenciales nunca se guardan aquí: el push real se hace por git desde el
    repositorio abapGit del equipo. Esto solo registra a dónde va el paquete.
    """
    __tablename__ = "sap_connections"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), unique=True, index=True, nullable=False)

    kind = Column(String(20), default="abapgit")     # abapgit | adt
    repo_url = Column(String(300))                    # URL del repo git abapGit
    branch = Column(String(80), default="main")
    sap_package = Column(String(60))
    transport_request = Column(String(40))
    adt_base_url = Column(String(300))                # base ADT/OData (informativo)

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
