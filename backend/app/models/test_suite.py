from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from app.core.database import Base


class TestSuite(Base):
    """Suite de pruebas unitarias ABAP Unit generada por IA."""
    __tablename__ = "test_suites"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), index=True)
    code_artifact_id = Column(Integer, ForeignKey("code_artifacts.id"))
    created_by = Column(Integer, ForeignKey("users.id"))

    framework = Column(String(30), default="abap_unit")
    test_code = Column(Text)                   # clase de test local ABAP Unit
    cases = Column(JSON, default=list)         # [{name, type, given, when, then}]
    mocks = Column(JSON, default=list)
    expected_coverage = Column(String(20))     # "80%"
    test_data = Column(JSON, default=list)
    execution_protocol = Column(Text)

    provider = Column(String(20))
    model = Column(String(60))
    created_at = Column(DateTime, default=datetime.utcnow)
