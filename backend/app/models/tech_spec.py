from datetime import datetime
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, JSON
from app.core.database import Base


class TechSpec(Base):
    """Especificación técnica generada por IA para un requerimiento."""
    __tablename__ = "tech_specs"

    id = Column(Integer, primary_key=True, index=True)
    requirement_id = Column(Integer, ForeignKey("requirements.id"), nullable=False, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), index=True)
    created_by = Column(Integer, ForeignKey("users.id"))

    # Bloques estructurados de la especificación (todos en JSON/Text)
    functional_description = Column(Text)
    technical_objective = Column(Text)
    assumptions = Column(JSON, default=list)
    sap_objects = Column(JSON, default=list)        # objetos involucrados
    standard_tables = Column(JSON, default=list)    # tablas estándar
    suggested_bapis = Column(JSON, default=list)
    badis_user_exits = Column(JSON, default=list)
    risks = Column(JSON, default=list)
    dependencies = Column(JSON, default=list)
    performance_notes = Column(Text)
    security_notes = Column(Text)
    transport_plan = Column(Text)
    rollback_plan = Column(Text)

    raw_markdown = Column(Text)   # versión completa en markdown para exportar

    created_at = Column(DateTime, default=datetime.utcnow)
