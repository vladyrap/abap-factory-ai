from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from app.core.database import Base


class AuditLog(Base):
    """Registro de auditoría: quién hizo qué y cuándo (acciones mutantes)."""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    user_email = Column(String(255))

    method = Column(String(10))
    path = Column(String(300))
    status = Column(Integer)
    action = Column(String(80))        # etiqueta legible derivada de la ruta
    request_id = Column(String(40))
    ip = Column(String(64))
    detail = Column(JSON, default=dict)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)
