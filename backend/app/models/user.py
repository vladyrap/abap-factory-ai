import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, ForeignKey
from app.core.database import Base


class UserRole(str, enum.Enum):
    admin = "admin"               # Administrador del sistema
    tech_lead = "tech_lead"       # Líder técnico
    consultant = "consultant"     # Consultor ABAP
    qa = "qa"                     # QA
    client_readonly = "client_readonly"  # Cliente solo lectura


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    # Rol legado (compatibilidad). Si role_id está seteado, manda el rol dinámico.
    role = Column(Enum(UserRole), default=UserRole.consultant, nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"))  # rol dinámico (RBAC a bajo nivel)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
