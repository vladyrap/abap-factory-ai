from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base


class Requirement(Base):
    """Requerimiento de desarrollo dentro de un proyecto. Punto de entrada del flujo."""
    __tablename__ = "requirements"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"))

    title = Column(String(250), nullable=False)
    description = Column(Text)                 # lo que el usuario describe que necesita

    # Selector de contexto SAP (snapshot al crear el requerimiento)
    sap_version = Column(String(40), default="S4HANA")
    module = Column(String(20))                # FI, MM, SD, PP, QM, PM, HR, CO, Basis, Integracion
    dev_type = Column(String(60))              # report, alv, salv, cds, amdp, rap, bapi, badi, idoc, ...
    complexity = Column(String(20), default="media")   # baja | media | alta | critica
    standard = Column(String(120))             # estándar requerido (Clean ABAP, 7.40+, etc.)
    restrictions = Column(Text)
    naming_convention = Column(String(200))
    transport_request = Column(String(40))
    sap_package = Column(String(60))
    extra_context = Column(JSON, default=dict) # cualquier campo adicional del selector

    status = Column(String(30), default="draft")  # draft | spec_ready | generated | tested | done

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = relationship("Project", back_populates="requirements")
