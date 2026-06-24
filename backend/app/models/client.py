from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base


class Client(Base):
    """Cliente SAP para el que se desarrollan los objetos ABAP."""
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    industry = Column(String(120))
    contact_name = Column(String(150))
    contact_email = Column(String(255))

    # Estándares y restricciones que el agente IA debe respetar
    naming_convention = Column(Text)     # ej: "ZAB_<modulo>_<obj>, prefijo Z/Y"
    coding_standards = Column(Text)      # Clean ABAP, no SELECT *, AUTHORITY-CHECK obligatorio...
    restrictions = Column(Text)          # restricciones del cliente (no modificar estándar, etc.)
    notes = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    projects = relationship("Project", back_populates="client", cascade="all, delete-orphan")
