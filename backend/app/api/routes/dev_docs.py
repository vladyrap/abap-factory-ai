from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.dev_document import DevDocument
from app.schemas.workbench import DevDocRequest
from app.api.deps import get_current_user, require_builder
from app.services.ai import dev_doc
from app.services.ai.engine import AIDisabledError

router = APIRouter(prefix="/dev-docs", tags=["Documento técnico"])


@router.post("/generate")
def generate(req: DevDocRequest, db: Session = Depends(get_db), user: User = Depends(require_builder)):
    ctx = req.sap_context.model_dump()
    client_id = req.client_id
    if not client_id and req.project_id:
        from app.models.project import Project
        proj = db.query(Project).filter(Project.id == req.project_id).first()
        client_id = proj.client_id if proj else None
    try:
        out = dev_doc.generate_document(
            db, description=req.description, sap_context=ctx,
            project_id=req.project_id, user_id=user.id, client_id=client_id,
        )
    except AIDisabledError as e:
        raise HTTPException(status_code=503, detail=str(e))

    if req.save and req.project_id:
        rec = DevDocument(
            project_id=req.project_id, requirement_id=req.requirement_id, created_by=user.id,
            title=out.get("title") or "Documento técnico", summary=out.get("summary"),
            objects=out.get("objects", []), steps=out.get("steps", []),
            transport_plan=out.get("transport_plan"), rollback_plan=out.get("rollback_plan"),
            provider=out.get("_meta", {}).get("provider"), model=out.get("_meta", {}).get("model"),
        )
        db.add(rec)
        db.commit()
        db.refresh(rec)
        out["id"] = rec.id
    return out


@router.get("/", dependencies=[Depends(get_current_user)])
def list_docs(project_id: int | None = None, db: Session = Depends(get_db)):
    q = db.query(DevDocument)
    if project_id:
        q = q.filter(DevDocument.project_id == project_id)
    rows = q.order_by(DevDocument.created_at.desc()).limit(100).all()
    return [{"id": r.id, "title": r.title, "objects": len(r.objects or []),
             "steps": len(r.steps or []), "created_at": r.created_at} for r in rows]


@router.get("/{doc_id}", dependencies=[Depends(get_current_user)])
def get_doc(doc_id: int, db: Session = Depends(get_db)):
    r = db.query(DevDocument).filter(DevDocument.id == doc_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    return {c.name: getattr(r, c.name) for c in r.__table__.columns}
