from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.code_inspection import CodeInspection
from app.schemas.workbench import InspectRequest
from app.api.deps import get_current_user, require_builder
from app.services.ai import inspector
from app.services.ai.engine import AIDisabledError

router = APIRouter(prefix="/inspector", tags=["Code Inspector / ATC"])


@router.post("/inspect")
def inspect(req: InspectRequest, db: Session = Depends(get_db), user: User = Depends(require_builder)):
    try:
        out = inspector.inspect_code(
            db, source_code=req.source_code,
            sap_context=req.sap_context.model_dump() if req.sap_context else None,
            project_id=req.project_id, user_id=user.id,
        )
    except AIDisabledError as e:
        raise HTTPException(status_code=503, detail=str(e))

    if req.save:
        rec = CodeInspection(
            project_id=req.project_id, code_artifact_id=req.code_artifact_id, created_by=user.id,
            source_code=req.source_code, score=out.get("score", 0),
            s4hana_compatible=out.get("s4hana_compatible"), findings=out.get("findings", []),
            rules_violated=out.get("rules_violated", []), recommendation=out.get("recommendation"),
            corrected_code=out.get("corrected_code"),
            provider=out.get("_meta", {}).get("provider"), model=out.get("_meta", {}).get("model"),
        )
        db.add(rec)
        db.commit()
        db.refresh(rec)
        out["id"] = rec.id
    return out


@router.get("/")
def list_inspections(project_id: int | None = None, db: Session = Depends(get_db),
                     _: User = Depends(get_current_user)):
    q = db.query(CodeInspection)
    if project_id:
        q = q.filter(CodeInspection.project_id == project_id)
    rows = q.order_by(CodeInspection.created_at.desc()).limit(100).all()
    return [
        {"id": r.id, "project_id": r.project_id, "score": r.score,
         "s4hana_compatible": r.s4hana_compatible, "findings_count": len(r.findings or []),
         "created_at": r.created_at}
        for r in rows
    ]
