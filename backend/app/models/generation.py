from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from app.core.database import Base


class Generation(Base):
    """Registro de una generación de código ABAP por un agente IA."""
    __tablename__ = "generations"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), index=True)
    requirement_id = Column(Integer, ForeignKey("requirements.id"), index=True)
    created_by = Column(Integer, ForeignKey("users.id"))

    agent_key = Column(String(50))          # abap_ecc | abap_s4 | webdynpro | ...
    provider = Column(String(20))           # claude | openai
    model = Column(String(60))

    sap_context = Column(JSON, default=dict)  # contexto SAP usado
    prompt = Column(Text)                     # prompt del usuario
    status = Column(String(20), default="ok") # ok | error

    tokens_in = Column(Integer, default=0)
    tokens_out = Column(Integer, default=0)
    cost_usd = Column(Float, default=0.0)
    latency_ms = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)

    artifacts = relationship("CodeArtifact", back_populates="generation")
