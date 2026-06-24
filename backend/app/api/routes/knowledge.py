from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user, require_builder
from app.models.user import User
from app.models.client_knowledge import ClientKnowledge, KNOWLEDGE_KINDS

router = APIRouter(prefix="/knowledge", tags=["Memoria del cliente (RAG)"])


class KnowledgeCreate(BaseModel):
    client_id: int
    kind: str = "snippet"
    title: str
    content: str


@router.get("/client/{client_id}", dependencies=[Depends(get_current_user)])
def list_knowledge(client_id: int, db: Session = Depends(get_db)):
    rows = (
        db.query(ClientKnowledge)
        .filter(ClientKnowledge.client_id == client_id)
        .order_by(ClientKnowledge.created_at.desc())
        .all()
    )
    return [{"id": r.id, "kind": r.kind, "title": r.title,
             "preview": (r.content or "")[:160], "created_at": r.created_at} for r in rows]


@router.post("/", status_code=201)
def add_knowledge(data: KnowledgeCreate, db: Session = Depends(get_db), user: User = Depends(require_builder)):
    if data.kind not in KNOWLEDGE_KINDS:
        raise HTTPException(status_code=400, detail=f"kind inválido. Use: {', '.join(KNOWLEDGE_KINDS)}")
    row = ClientKnowledge(client_id=data.client_id, created_by=user.id,
                          kind=data.kind, title=data.title, content=data.content)
    db.add(row)
    db.commit()
    db.refresh(row)
    return {"id": row.id}


@router.delete("/{kid}", dependencies=[Depends(require_builder)])
def delete_knowledge(kid: int, db: Session = Depends(get_db)):
    row = db.query(ClientKnowledge).filter(ClientKnowledge.id == kid).first()
    if not row:
        raise HTTPException(status_code=404, detail="No encontrado")
    db.delete(row)
    db.commit()
    return {"ok": True}
