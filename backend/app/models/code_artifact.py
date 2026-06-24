from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class CodeArtifact(Base):
    """Código ABAP generado/editado. Soporta versionado vía parent_id."""
    __tablename__ = "code_artifacts"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), index=True)
    requirement_id = Column(Integer, ForeignKey("requirements.id"), index=True)
    generation_id = Column(Integer, ForeignKey("generations.id"))
    created_by = Column(Integer, ForeignKey("users.id"))

    name = Column(String(120), nullable=False)         # ZAB_REPORT_001
    dev_type = Column(String(60))                      # report, salv, cds, ...
    language = Column(String(20), default="abap_oo")   # abap_classic | abap_oo
    code = Column(Text, nullable=False)
    explanation = Column(Text)                         # explicación del código

    version = Column(Integer, default=1)
    parent_id = Column(Integer, ForeignKey("code_artifacts.id"))  # versión anterior
    status = Column(String(30), default="generated")   # generated | edited | approved

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    generation = relationship("Generation", back_populates="artifacts")
