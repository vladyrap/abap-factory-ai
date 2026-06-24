from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from app.core.database import Base


class Migration(Base):
    """Migración de código de SAP ECC a S/4HANA / ABAP Cloud."""
    __tablename__ = "migrations"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), index=True)
    created_by = Column(Integer, ForeignKey("users.id"))

    source_code = Column(Text, nullable=False)
    target = Column(String(40), default="S4HANA")     # S4HANA | S4HANA_CLOUD_PUBLIC | BTP_ABAP

    migrated_code = Column(Text)
    changes = Column(JSON, default=list)              # [{area, before, after, reason}]
    simplification_items = Column(JSON, default=list) # [{item, table, note}]
    compatibility = Column(String(20))                # ok | parcial | manual
    notes = Column(Text)
    manual_steps = Column(JSON, default=list)

    provider = Column(String(20))
    model = Column(String(60))
    created_at = Column(DateTime, default=datetime.utcnow)
