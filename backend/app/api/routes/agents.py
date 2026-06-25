import re
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user, require_perm
from app.models.user import User
from app.models.agent_config import AgentConfig
from app.schemas.workbench import AgentConfigUpdate
from app.services.ai.agents import AGENTS
from app.services.ai.provider import get_provider

router = APIRouter(prefix="/agents", tags=["Agentes IA"])

require_agents_admin = require_perm("agents.manage")


class AgentCreate(BaseModel):
    key: str
    name: str
    description: Optional[str] = None
    provider: str = "claude"
    model: Optional[str] = None
    temperature: float = 0.2
    max_tokens: int = 4000
    system_prompt: str


def _row_to_dict(cfg: AgentConfig) -> dict:
    return {
        "key": cfg.agent_key, "name": cfg.name, "description": cfg.description,
        "provider": cfg.provider, "model": cfg.model or "(default del proveedor)",
        "temperature": cfg.temperature, "max_tokens": cfg.max_tokens,
        "system_prompt": cfg.system_prompt, "is_active": cfg.is_active,
        "is_system": cfg.is_system, "customized": True,
    }


@router.get("/", dependencies=[Depends(get_current_user)])
def list_agents(db: Session = Depends(get_db)):
    """Lista los agentes desde BD; si falta alguno del catálogo en código, lo incluye."""
    rows = {c.agent_key: c for c in db.query(AgentConfig).all()}
    out = []
    for key, cfg in rows.items():
        out.append(_row_to_dict(cfg))
    # agentes del catálogo en código aún no sembrados en BD (p.ej. en tests)
    for key, a in AGENTS.items():
        if key not in rows:
            out.append({
                "key": key, "name": a.name, "description": a.description,
                "provider": a.default_provider, "model": a.default_model or "(default del proveedor)",
                "temperature": a.default_temperature, "max_tokens": a.default_max_tokens,
                "system_prompt": a.system_prompt, "is_active": True,
                "is_system": True, "customized": False,
            })
    out.sort(key=lambda x: (not x["is_system"], x["name"]))
    return out


@router.get("/providers/status", dependencies=[Depends(get_current_user)])
def providers_status():
    return {
        "claude": get_provider("claude").is_enabled(),
        "openai": get_provider("openai").is_enabled(),
        "gemini": get_provider("gemini").is_enabled(),
    }


@router.post("/", status_code=201, dependencies=[Depends(require_agents_admin)])
def create_agent(data: AgentCreate, db: Session = Depends(get_db)):
    key = data.key.strip().lower()
    if not re.fullmatch(r"[a-z][a-z0-9_]{2,40}", key):
        raise HTTPException(status_code=400, detail="Key inválido: usa minúsculas, números y _ (3-40).")
    if key in AGENTS or db.query(AgentConfig).filter(AgentConfig.agent_key == key).first():
        raise HTTPException(status_code=400, detail="Ya existe un agente con ese key")
    if data.provider not in ("claude", "openai", "gemini"):
        raise HTTPException(status_code=400, detail="Proveedor no soportado")
    cfg = AgentConfig(
        agent_key=key, name=data.name, description=data.description, provider=data.provider,
        model=data.model, temperature=data.temperature, max_tokens=data.max_tokens,
        system_prompt=data.system_prompt, is_active=True, is_system=False,
    )
    db.add(cfg)
    db.commit()
    return {"key": key}


@router.put("/{agent_key}", dependencies=[Depends(require_agents_admin)])
def update_agent(agent_key: str, data: AgentConfigUpdate, db: Session = Depends(get_db)):
    cfg = db.query(AgentConfig).filter(AgentConfig.agent_key == agent_key).first()
    if not cfg:
        # primera edición de un agente del catálogo en código → materializar fila
        code = AGENTS.get(agent_key)
        if not code:
            raise HTTPException(status_code=404, detail="Agente desconocido")
        cfg = AgentConfig(agent_key=agent_key, name=code.name, description=code.description,
                          provider=code.default_provider, model=code.default_model,
                          temperature=code.default_temperature, max_tokens=code.default_max_tokens,
                          system_prompt=code.system_prompt, is_active=True, is_system=True)
        db.add(cfg)
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(cfg, k, v)
    db.commit()
    return {"ok": True, "agent_key": agent_key}


@router.delete("/{agent_key}", dependencies=[Depends(require_agents_admin)])
def delete_agent(agent_key: str, db: Session = Depends(get_db)):
    if agent_key in AGENTS:
        raise HTTPException(status_code=400, detail="No se puede eliminar un agente del sistema")
    cfg = db.query(AgentConfig).filter(AgentConfig.agent_key == agent_key).first()
    if not cfg:
        raise HTTPException(status_code=404, detail="Agente no encontrado")
    if cfg.is_system:
        raise HTTPException(status_code=400, detail="No se puede eliminar un agente del sistema")
    db.delete(cfg)
    db.commit()
    return {"ok": True}
