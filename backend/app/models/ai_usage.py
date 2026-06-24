from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from app.core.database import Base


class AIUsage(Base):
    """Registro unificado de TODO consumo de IA (generación, dump, inspector, tests, spec).

    Alimenta el dashboard de costos en USD y CLP, por usuario y por proyecto.
    """
    __tablename__ = "ai_usage"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)

    operation = Column(String(40))     # generate | dump | inspect | unit_test | protocol | spec | explain | refactor
    agent_key = Column(String(50))
    provider = Column(String(20))
    model = Column(String(60))

    tokens_in = Column(Integer, default=0)
    tokens_out = Column(Integer, default=0)
    cost_usd = Column(Float, default=0.0)
    cost_clp = Column(Float, default=0.0)
    latency_ms = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)
