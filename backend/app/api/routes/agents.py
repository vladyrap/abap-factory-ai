from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user, require_admin
from app.models.user import User
from app.models.agent_config import AgentConfig
from app.schemas.workbench import AgentConfigUpdate
from app.services.ai.agents import AGENTS
from app.services.ai.provider import get_provider

router = APIRouter(prefix="/agents", tags=["Agentes IA"])


@router.get("/", dependencies=[Depends(get_current_user)])
def list_agents(db: Session = Depends(get_db)):
    """Devuelve los 6 agentes con su configuración efectiva (BD override > default catálogo)."""
    overrides = {c.agent_key: c for c in db.query(AgentConfig).all()}
    out = []
    for key, agent in AGENTS.items():
        cfg = overrides.get(key)
        out.append({
            "key": key,
            "name": agent.name,
            "description": agent.description,
            "provider": (cfg.provider if cfg else None) or agent.default_provider,
            "model": (cfg.model if cfg else None) or agent.default_model or "(default del proveedor)",
            "temperature": cfg.temperature if cfg else agent.default_temperature,
            "max_tokens": cfg.max_tokens if cfg else agent.default_max_tokens,
            "system_prompt": (cfg.system_prompt if cfg else None) or agent.system_prompt,
            "is_active": cfg.is_active if cfg else True,
            "customized": cfg is not None,
        })
    return out


@router.get("/providers/status", dependencies=[Depends(get_current_user)])
def providers_status():
    return {
        "claude": get_provider("claude").is_enabled(),
        "openai": get_provider("openai").is_enabled(),
    }


@router.put("/{agent_key}", dependencies=[Depends(require_admin)])
def update_agent(agent_key: str, data: AgentConfigUpdate, db: Session = Depends(get_db)):
    if agent_key not in AGENTS:
        raise HTTPException(status_code=404, detail="Agente desconocido")
    agent = AGENTS[agent_key]
    cfg = db.query(AgentConfig).filter(AgentConfig.agent_key == agent_key).first()
    if not cfg:
        cfg = AgentConfig(agent_key=agent_key, name=agent.name, description=agent.description,
                          provider=agent.default_provider, model=agent.default_model,
                          temperature=agent.default_temperature, max_tokens=agent.default_max_tokens,
                          system_prompt=agent.system_prompt)
        db.add(cfg)
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(cfg, k, v)
    db.commit()
    db.refresh(cfg)
    return {"ok": True, "agent_key": agent_key}
