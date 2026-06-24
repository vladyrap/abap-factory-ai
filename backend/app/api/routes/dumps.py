from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.dump_analysis import DumpAnalysis
from app.schemas.workbench import DumpRequest, DumpResponse
from app.api.deps import get_current_user, require_builder
from app.services.ai import dump_solver
from app.services.ai.engine import AIDisabledError

router = APIRouter(prefix="/dumps", tags=["Analizador de Dumps"])


@router.post("/analyze", response_model=DumpResponse)
def analyze(req: DumpRequest, db: Session = Depends(get_db), user: User = Depends(require_builder)):
    try:
        out = dump_solver.analyze_dump(
            db, raw_dump=req.raw_dump, project_id=req.project_id, user_id=user.id,
            sap_context=req.sap_context.model_dump() if req.sap_context else None,
        )
    except AIDisabledError as e:
        raise HTTPException(status_code=503, detail=str(e))

    record = None
    if req.save:
        record = DumpAnalysis(
            project_id=req.project_id, created_by=user.id, raw_dump=req.raw_dump,
            dump_type=out.get("dump_type"), severity=out.get("severity"),
            program=out.get("program"), include=out.get("include"), line=str(out.get("line") or ""),
            sap_object=out.get("sap_object"), root_cause=out.get("root_cause"),
            solution=out.get("solution"), fixed_code=out.get("fixed_code"),
            checklist=out.get("checklist", []), suggested_tests=out.get("suggested_tests", []),
            provider=out.get("_meta", {}).get("provider"), model=out.get("_meta", {}).get("model"),
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    return DumpResponse(**{k: v for k, v in out.items() if k != "_meta"})


@router.get("/", response_model=list[DumpResponse], dependencies=[Depends(get_current_user)])
def list_dumps(project_id: int | None = None, db: Session = Depends(get_db)):
    q = db.query(DumpAnalysis)
    if project_id:
        q = q.filter(DumpAnalysis.project_id == project_id)
    return q.order_by(DumpAnalysis.created_at.desc()).limit(200).all()


@router.get("/{dump_id}", response_model=DumpResponse, dependencies=[Depends(get_current_user)])
def get_dump(dump_id: int, db: Session = Depends(get_db)):
    rec = db.query(DumpAnalysis).filter(DumpAnalysis.id == dump_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Análisis no encontrado")
    return rec
