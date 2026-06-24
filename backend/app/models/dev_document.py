from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from app.core.database import Base


class DevDocument(Base):
    """Documento técnico de un desarrollo: inventario de objetos + paso a paso.

    Detalla CADA objeto que se tocará/creará (nombre, tipo, acción, paquete) y la
    guía de construcción paso a paso. Exportable a PDF.
    """
    __tablename__ = "dev_documents"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), index=True)
    requirement_id = Column(Integer, ForeignKey("requirements.id"))
    created_by = Column(Integer, ForeignKey("users.id"))

    title = Column(String(250), nullable=False)
    summary = Column(Text)
    # objects: [{name, type, action(crear|modificar|usar), package, description, dependencies}]
    objects = Column(JSON, default=list)
    # steps: [{n, title, detail, objects}]
    steps = Column(JSON, default=list)
    transport_plan = Column(Text)
    rollback_plan = Column(Text)

    provider = Column(String(20))
    model = Column(String(60))
    created_at = Column(DateTime, default=datetime.utcnow)
