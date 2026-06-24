from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from app.core.database import Base


# Tipos de conocimiento ingerido del cliente
KNOWLEDGE_KINDS = ("z_object", "ddic", "standard", "snippet", "doc")


class ClientKnowledge(Base):
    """Fragmento de conocimiento del landscape del cliente para RAG.

    Permite que el agente genere código consistente con los objetos, diccionario
    de datos y estándares existentes del cliente, sin que el consultor los conozca.
    """
    __tablename__ = "client_knowledge"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False, index=True)
    created_by = Column(Integer, ForeignKey("users.id"))

    kind = Column(String(20), default="snippet")   # ver KNOWLEDGE_KINDS
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
