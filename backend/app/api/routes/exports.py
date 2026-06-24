from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.code_artifact import CodeArtifact
from app.models.tech_spec import TechSpec
from app.models.dump_analysis import DumpAnalysis
from app.models.code_inspection import CodeInspection
from app.models.test_protocol import TestProtocol
from app.models.test_suite import TestSuite
from app.models.project import Project
from app.models.requirement import Requirement
from app.models.migration import Migration
from app.models.dev_document import DevDocument
from app.services import exports, abapgit


def _as_dict(obj):
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns} if obj else None

router = APIRouter(prefix="/exports", tags=["Exportaciones"], dependencies=[Depends(get_current_user)])


def _stream(data: bytes, media: str, filename: str):
    return StreamingResponse(
        iter([data]), media_type=media,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/artifact/{artifact_id}.abap")
def export_abap(artifact_id: int, db: Session = Depends(get_db)):
    art = db.query(CodeArtifact).filter(CodeArtifact.id == artifact_id).first()
    if not art:
        raise HTTPException(status_code=404, detail="Artefacto no encontrado")
    data = exports.code_to_abap(art.name, art.code)
    return _stream(data, "text/plain", f"{art.name}.abap")


@router.get("/spec/{spec_id}.pdf")
def export_spec(spec_id: int, db: Session = Depends(get_db)):
    spec = db.query(TechSpec).filter(TechSpec.id == spec_id).first()
    if not spec:
        raise HTTPException(status_code=404, detail="Spec no encontrada")
    payload = {c.name: getattr(spec, c.name) for c in spec.__table__.columns}
    data = exports.spec_to_pdf(payload)
    return _stream(data, "application/pdf", f"spec_{spec_id}.pdf")


@router.get("/dump/{dump_id}.pdf")
def export_dump(dump_id: int, db: Session = Depends(get_db)):
    d = db.query(DumpAnalysis).filter(DumpAnalysis.id == dump_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Dump no encontrado")
    payload = {c.name: getattr(d, c.name) for c in d.__table__.columns}
    data = exports.dump_to_pdf(payload)
    return _stream(data, "application/pdf", f"dump_{dump_id}.pdf")


@router.get("/inspection/{inspection_id}.pdf")
def export_inspection(inspection_id: int, db: Session = Depends(get_db)):
    ins = db.query(CodeInspection).filter(CodeInspection.id == inspection_id).first()
    if not ins:
        raise HTTPException(status_code=404, detail="Inspección no encontrada")
    payload = {c.name: getattr(ins, c.name) for c in ins.__table__.columns}
    data = exports.inspection_to_pdf(payload)
    return _stream(data, "application/pdf", f"inspection_{inspection_id}.pdf")


@router.get("/documentation/{project_id}.pdf")
def export_documentation(project_id: int, requirement_id: int | None = None, db: Session = Depends(get_db)):
    """Documentación completa: spec + código + inspección + pruebas de un proyecto/requerimiento."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")

    art_q = db.query(CodeArtifact).filter(CodeArtifact.project_id == project_id)
    ins_q = db.query(CodeInspection).filter(CodeInspection.project_id == project_id)
    ts_q = db.query(TestSuite).filter(TestSuite.project_id == project_id)
    spec = None
    requirement = None
    if requirement_id:
        requirement = db.query(Requirement).filter(Requirement.id == requirement_id).first()
        art_q = art_q.filter(CodeArtifact.requirement_id == requirement_id)
        spec = db.query(TechSpec).filter(TechSpec.requirement_id == requirement_id).order_by(TechSpec.id.desc()).first()

    data = exports.documentation_pdf(
        project=_as_dict(project), requirement=_as_dict(requirement), spec=_as_dict(spec),
        artifacts=[_as_dict(a) for a in art_q.order_by(CodeArtifact.created_at).all()],
        inspections=[_as_dict(i) for i in ins_q.order_by(CodeInspection.created_at).all()],
        test_suites=[_as_dict(t) for t in ts_q.order_by(TestSuite.created_at).all()],
    )
    return _stream(data, "application/pdf", f"documentacion_proyecto_{project_id}.pdf")


@router.get("/project/{project_id}/abapgit.zip")
def export_abapgit(project_id: int, db: Session = Depends(get_db)):
    """Paquete abapGit (.zip) con todos los artefactos de código del proyecto."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    arts = db.query(CodeArtifact).filter(CodeArtifact.project_id == project_id).order_by(CodeArtifact.created_at).all()
    if not arts:
        raise HTTPException(status_code=404, detail="El proyecto no tiene artefactos de código")
    data = abapgit.build_zip(_as_dict(project), arts)
    return _stream(data, "application/zip", f"abapgit_proyecto_{project_id}.zip")


@router.get("/migration/{mig_id}.pdf")
def export_migration(mig_id: int, db: Session = Depends(get_db)):
    m = db.query(Migration).filter(Migration.id == mig_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Migración no encontrada")
    data = exports.migration_to_pdf(_as_dict(m))
    return _stream(data, "application/pdf", f"migracion_{mig_id}.pdf")


@router.get("/dev-doc/{doc_id}.pdf")
def export_dev_doc(doc_id: int, db: Session = Depends(get_db)):
    d = db.query(DevDocument).filter(DevDocument.id == doc_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    data = exports.dev_document_pdf(_as_dict(d))
    return _stream(data, "application/pdf", f"documento_tecnico_{doc_id}.pdf")


@router.get("/protocol/{protocol_id}.xlsx")
def export_protocol_xlsx(protocol_id: int, db: Session = Depends(get_db)):
    p = db.query(TestProtocol).filter(TestProtocol.id == protocol_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Protocolo no encontrado")
    data = exports.test_cases_to_xlsx(p.cases or [], p.name)
    return _stream(data, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                   f"protocolo_{protocol_id}.xlsx")
