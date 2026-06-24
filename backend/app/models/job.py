from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Text
from app.core.database import Base


# Tipos de job soportados
JOB_TYPES = ("batch_inspect", "batch_generate")


class Job(Base):
    """Proceso asíncrono ejecutado en background por APScheduler."""
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), index=True)
    created_by = Column(Integer, ForeignKey("users.id"))

    job_type = Column(String(40), nullable=False)     # ver JOB_TYPES
    status = Column(String(20), default="pending")    # pending | running | done | error
    params = Column(JSON, default=dict)
    result = Column(JSON, default=dict)
    error = Column(Text)

    total = Column(Integer, default=0)
    processed = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    finished_at = Column(DateTime)
