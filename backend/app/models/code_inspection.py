from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Float
from app.core.database import Base


class CodeInspection(Base):
    """Resultado del Code Inspector / ATC Advisor simulado por IA."""
    __tablename__ = "code_inspections"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), index=True)
    code_artifact_id = Column(Integer, ForeignKey("code_artifacts.id"))
    created_by = Column(Integer, ForeignKey("users.id"))

    source_code = Column(Text, nullable=False)
    score = Column(Float, default=0.0)         # 0-100 score técnico
    s4hana_compatible = Column(String(20))     # si | parcial | no

    findings = Column(JSON, default=list)      # [{rule, severity, line, message, suggestion}]
    rules_violated = Column(JSON, default=list)
    recommendation = Column(Text)
    corrected_code = Column(Text)

    provider = Column(String(20))
    model = Column(String(60))
    created_at = Column(DateTime, default=datetime.utcnow)
