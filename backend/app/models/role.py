from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON
from app.core.database import Base


class Role(Base):
    """Rol dinámico: un nombre + un conjunto de permisos granulares.

    is_system marca los roles base (no se pueden borrar). permissions es una lista
    de claves de app.core.permissions (o ["*"] para superusuario).
    """
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(80), unique=True, nullable=False, index=True)
    description = Column(Text)
    is_system = Column(Boolean, default=False)
    permissions = Column(JSON, default=list)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
