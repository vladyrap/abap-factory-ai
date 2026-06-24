from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.test_suite import TestSuite
from app.models.test_protocol import TestProtocol
from app.schemas.workbench import UnitTestRequest, ProtocolRequest
from app.api.deps import get_current_user, require_qa
from app.services.ai import test_gen
from app.services.ai.engine import AIDisabledError

router = APIRouter(prefix="/tests", tags=["Pruebas ABAP"])


@router.post("/unit")
def generate_unit(req: UnitTestRequest, db: Session = Depends(get_db), user: User = Depends(require_qa)):
    try:
        out = test_gen.generate_unit_tests(
            db, source_code=req.source_code,
            sap_context=req.sap_context.model_dump() if req.sap_context else None,
            project_id=req.project_id, user_id=user.id,
        )
    except AIDisabledError as e:
        raise HTTPException(status_code=503, detail=str(e))

    if req.save:
        rec = TestSuite(
            project_id=req.project_id, code_artifact_id=req.code_artifact_id, created_by=user.id,
            test_code=out.get("test_code"), cases=out.get("cases", []), mocks=out.get("mocks", []),
            expected_coverage=out.get("expected_coverage"), test_data=out.get("test_data", []),
            execution_protocol=out.get("execution_protocol"),
            provider=out.get("_meta", {}).get("provider"), model=out.get("_meta", {}).get("model"),
        )
        db.add(rec)
        db.commit()
        db.refresh(rec)
        out["id"] = rec.id
    return out


@router.post("/protocol")
def generate_protocol(req: ProtocolRequest, db: Session = Depends(get_db), user: User = Depends(require_qa)):
    try:
        out = test_gen.generate_protocol(
            db, description=req.description, protocol_type=req.protocol_type,
            sap_context=req.sap_context.model_dump() if req.sap_context else None,
            project_id=req.project_id, user_id=user.id,
        )
    except AIDisabledError as e:
        raise HTTPException(status_code=503, detail=str(e))

    if req.save:
        rec = TestProtocol(
            project_id=req.project_id, requirement_id=req.requirement_id, created_by=user.id,
            name=req.name or f"Protocolo {req.protocol_type}", protocol_type=req.protocol_type,
            cases=out.get("cases", []),
            provider=out.get("_meta", {}).get("provider"), model=out.get("_meta", {}).get("model"),
        )
        db.add(rec)
        db.commit()
        db.refresh(rec)
        out["id"] = rec.id
    return out


@router.get("/suites", dependencies=[Depends(get_current_user)])
def list_suites(project_id: int | None = None, db: Session = Depends(get_db)):
    q = db.query(TestSuite)
    if project_id:
        q = q.filter(TestSuite.project_id == project_id)
    rows = q.order_by(TestSuite.created_at.desc()).limit(100).all()
    return [{"id": r.id, "project_id": r.project_id, "cases": len(r.cases or []),
             "expected_coverage": r.expected_coverage, "created_at": r.created_at} for r in rows]


@router.get("/protocols", dependencies=[Depends(get_current_user)])
def list_protocols(project_id: int | None = None, db: Session = Depends(get_db)):
    q = db.query(TestProtocol)
    if project_id:
        q = q.filter(TestProtocol.project_id == project_id)
    return q.order_by(TestProtocol.created_at.desc()).limit(100).all()


@router.get("/protocols/{protocol_id}", dependencies=[Depends(get_current_user)])
def get_protocol(protocol_id: int, db: Session = Depends(get_db)):
    rec = db.query(TestProtocol).filter(TestProtocol.id == protocol_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Protocolo no encontrado")
    return rec
