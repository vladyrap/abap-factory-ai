from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from app.core.database import Base


class DumpAnalysis(Base):
    """Análisis de un dump ST22 pegado por el usuario."""
    __tablename__ = "dump_analyses"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), index=True)
    created_by = Column(Integer, ForeignKey("users.id"))

    raw_dump = Column(Text, nullable=False)

    dump_type = Column(String(80))          # OBJECTS_OBJREF_NOT_ASSIGNED, TIME_OUT, ...
    severity = Column(String(20))           # baja | media | alta | critica

    program = Column(String(120))
    include = Column(String(120))
    line = Column(String(20))
    sap_object = Column(String(120))

    root_cause = Column(Text)
    solution = Column(Text)
    fixed_code = Column(Text)
    checklist = Column(JSON, default=list)
    suggested_tests = Column(JSON, default=list)

    provider = Column(String(20))
    model = Column(String(60))
    created_at = Column(DateTime, default=datetime.utcnow)
