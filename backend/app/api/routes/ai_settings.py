from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import require_perm
from app.models.user import User
from app.services.ai import credentials
from app.services.ai.provider import get_provider

router = APIRouter(prefix="/admin/ai-settings", tags=["Credenciales IA"])

require_ai_admin = require_perm("agents.manage")

# Guía paso a paso para obtener cada API key (se muestra en la web)
GUIDE = {
    "gemini": {
        "name": "Google Gemini", "free": True,
        "url": "https://aistudio.google.com/apikey",
        "steps": [
            "Entra a https://aistudio.google.com/apikey con tu cuenta de Google.",
            "Pulsa 'Create API key' (Crear clave de API).",
            "Elige o crea un proyecto de Google Cloud (sirve el gratuito).",
            "Copia la clave generada (empieza con 'AIza...').",
            "Pégala abajo en 'Gemini' y pulsa Guardar.",
            "Tip: la capa gratuita tiene límites de velocidad; ideal para probar.",
        ],
    },
    "anthropic": {
        "name": "Claude (Anthropic)", "free": False,
        "url": "https://console.anthropic.com/settings/keys",
        "steps": [
            "Entra a https://console.anthropic.com y crea una cuenta.",
            "Ve a Settings → API Keys.",
            "Pulsa 'Create Key', ponle un nombre y cópiala (empieza con 'sk-ant-...').",
            "Carga saldo en Billing (no hay capa gratuita estable).",
            "Pégala abajo en 'Claude' y pulsa Guardar.",
        ],
    },
    "openai": {
        "name": "OpenAI", "free": False,
        "url": "https://platform.openai.com/api-keys",
        "steps": [
            "Entra a https://platform.openai.com/api-keys e inicia sesión.",
            "Pulsa 'Create new secret key' y cópiala (empieza con 'sk-...').",
            "Configura facturación en Billing.",
            "Pégala abajo en 'OpenAI' y pulsa Guardar.",
        ],
    },
}


class AISettingsUpdate(BaseModel):
    anthropic_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    default_provider: Optional[str] = None


@router.get("/", dependencies=[Depends(require_ai_admin)])
def get_settings():
    """Estado de cada proveedor (sin exponer la clave) + guía paso a paso."""
    provs = []
    for p in credentials.PROVIDERS:
        g = GUIDE[p]
        provs.append({
            "key": p, "name": g["name"], "free": g["free"],
            "configured": bool(credentials.get_key(p)),
            "source": credentials.key_source(p),     # bd | env | None
            "masked": credentials.masked(p),
            "get_key_url": g["url"], "steps": g["steps"],
        })
    return {"providers": provs, "default_provider": credentials.default_provider()}


@router.put("/", dependencies=[Depends(require_ai_admin)])
def update_settings(data: AISettingsUpdate, db: Session = Depends(get_db)):
    if data.anthropic_api_key is not None:
        credentials.set_key(db, "anthropic", data.anthropic_api_key.strip() or None)
    if data.openai_api_key is not None:
        credentials.set_key(db, "openai", data.openai_api_key.strip() or None)
    if data.gemini_api_key is not None:
        credentials.set_key(db, "gemini", data.gemini_api_key.strip() or None)
    if data.default_provider:
        credentials.set_default_provider(db, data.default_provider)
    return {"ok": True}


@router.post("/test/{provider}", dependencies=[Depends(require_ai_admin)])
def test_provider(provider: str):
    """Prueba real: hace una mini llamada para verificar que la key funciona."""
    if provider not in credentials.PROVIDERS:
        raise HTTPException(status_code=400, detail="Proveedor inválido")
    prov = get_provider("claude" if provider == "anthropic" else provider)
    if not prov.is_enabled():
        raise HTTPException(status_code=400, detail="No hay clave configurada para este proveedor")
    try:
        res = prov.complete(system="Eres un test.", user_prompt="Responde solo: OK", max_tokens=5, temperature=0)
        return {"ok": True, "model": res.model, "reply": (res.text or "").strip()[:40]}
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"Falló la prueba: {str(e)[:200]}")
