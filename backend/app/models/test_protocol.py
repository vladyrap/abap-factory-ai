from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from app.core.database import Base


# Tipos de protocolo de prueba soportados
PROTOCOL_TYPES = (
    "unitaria", "tecnica", "funcional", "integracion",
    "regresion", "performance", "uat",
)


class TestProtocol(Base):
    """Protocolo de prueba (documento) con uno o varios casos de prueba."""
    __tablename__ = "test_protocols"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), index=True)
    requirement_id = Column(Integer, ForeignKey("requirements.id"))
    created_by = Column(Integer, ForeignKey("users.id"))

    name = Column(String(200), nullable=False)
    protocol_type = Column(String(30), default="funcional")  # ver PROTOCOL_TYPES
    environment = Column(String(10), default="QAS")
    responsible = Column(String(150))

    # Cada caso: {case_id, name, preconditions, input_data, steps, expected_result,
    #             actual_result, status, evidence_required, observations}
    cases = Column(JSON, default=list)

    provider = Column(String(20))
    model = Column(String(60))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
