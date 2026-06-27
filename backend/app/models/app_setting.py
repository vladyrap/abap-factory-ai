from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from app.core.database import Base


class AppSetting(Base):
    """Configuración del sistema en BD (clave/valor). Los secretos se guardan cifrados."""
    __tablename__ = "app_settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(80), unique=True, index=True, nullable=False)
    value = Column(Text)              # cifrado para secretos (API keys)
    is_secret = Column(Integer, default=0)  # 1 = el value está cifrado
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
