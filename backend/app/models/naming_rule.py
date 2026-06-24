from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from app.core.database import Base


# Tipos de objeto SAP que admiten convención de nombre (no toda empresa usa lo mismo)
NAMING_OBJECT_TYPES = (
    "table", "structure", "data_element", "domain", "table_type",
    "class", "interface", "report", "include", "function_group", "function_module",
    "cds_interface", "cds_projection", "behavior", "service_def", "service_binding",
    "package", "message_class", "transaction", "badi", "enhancement", "amdp",
)


class NamingRule(Base):
    """Regla de nomenclatura por cliente y tipo de objeto.

    El patrón usa marcadores entre llaves que se sustituyen dinámicamente, p.ej.:
      "Z{MODULE}_{NAME}"          -> ZFI_PARTIDAS
      "ZCL_{AREA}_{NAME}"         -> ZCL_FI_PARTIDAS
      "ZI_{NAME}" / "ZC_{NAME}"   -> CDS de interfaz / proyección
    """
    __tablename__ = "naming_rules"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False, index=True)
    created_by = Column(Integer, ForeignKey("users.id"))

    object_type = Column(String(40), nullable=False)   # ver NAMING_OBJECT_TYPES
    pattern = Column(String(120), nullable=False)       # "Z{MODULE}_{NAME}"
    example = Column(String(120))                       # "ZFI_PARTIDAS"
    description = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)
