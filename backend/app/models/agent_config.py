from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float
from app.core.database import Base


class AgentConfig(Base):
    """Configuración persistida y editable de cada agente IA (pantalla 'Configuración de agentes').

    Si una fila no existe para un agent_key, se usa el valor por defecto del catálogo en código.
    """
    __tablename__ = "agent_configs"

    id = Column(Integer, primary_key=True, index=True)
    agent_key = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(120), nullable=False)
    description = Column(Text)

    provider = Column(String(20), default="claude")   # claude | openai
    model = Column(String(60))
    temperature = Column(Float, default=0.2)
    max_tokens = Column(Integer, default=4000)
    system_prompt = Column(Text)

    is_active = Column(Boolean, default=True)
    is_system = Column(Boolean, default=False)   # agentes base (no se pueden eliminar)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
