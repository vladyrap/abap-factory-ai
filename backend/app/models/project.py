from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base


class Project(Base):
    """Proyecto ABAP de un cliente. Agrupa requerimientos, generaciones, dumps, etc."""
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    owner_user_id = Column(Integer, ForeignKey("users.id"))

    name = Column(String(200), nullable=False)
    code = Column(String(60))            # código interno del proyecto
    description = Column(Text)

    # Contexto SAP por defecto del proyecto (se puede sobreescribir por generación)
    sap_version = Column(String(40), default="S4HANA")   # ECC | S4HANA | S4HANA_CLOUD_PRIVATE | S4HANA_CLOUD_PUBLIC
    modules = Column(JSON, default=list)                 # ["FI","MM","SD",...]
    sap_package = Column(String(60))
    transport_request = Column(String(40))
    mandante = Column(String(10))                        # cliente/mandante SAP (000, 100...)
    environment = Column(String(10), default="DEV")      # DEV | QAS | PRD

    status = Column(String(30), default="active")        # active | on_hold | closed

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    client = relationship("Client", back_populates="projects")
    requirements = relationship("Requirement", back_populates="project", cascade="all, delete-orphan")
