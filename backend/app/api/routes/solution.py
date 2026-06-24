from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.models.generation import Generation
from app.models.code_artifact import CodeArtifact
from app.models.tech_spec import TechSpec
from app.models.test_suite import TestSuite
from app.models.dev_document import DevDocument
from app.schemas.workbench import SolutionRequest
from app.api.deps import get_current_user, require_builder
from app.services.ai import solution
from app.services.ai.engine import AIDisabledError
from app.services import extract_text

router = APIRouter(prefix="/solution", tags=["Requerimiento → Solución"])


@router.post("/extract-file")
async def extract_file(file: UploadFile = File(...), _: User = Depends(require_builder)):
    """Lee un requerimiento desde PDF / Word / texto y devuelve su contenido."""
    content = await file.read()
    if len(content) > 8 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Archivo demasiado grande (máx 8MB).")
    try:
        text = extract_text.extract(file.filename, content)
    except extract_text.UnsupportedFile as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:  # noqa: BLE001
        raise HTTPException(status_code=422, detail="No se pudo leer el archivo.")
    if not text.strip():
        raise HTTPException(status_code=422, detail="El archivo no contiene texto legible.")
    return {"filename": file.filename, "text": text[: settings.MAX_INPUT_CHARS]}


@router.post("/build")
def build_solution(req: SolutionRequest, db: Session = Depends(get_db), user: User = Depends(require_builder)):
    """Lee un requerimiento funcional, clasifica qué se necesita y lo resuelve end-to-end."""
    client_id = req.client_id
    if not client_id and req.project_id:
        from app.models.project import Project
        proj = db.query(Project).filter(Project.id == req.project_id).first()
        client_id = proj.client_id if proj else None
    try:
        out = solution.build(
            db, requirement_text=req.requirement_text, existing_code=req.existing_code,
            sap_context_override=req.sap_context.model_dump() if req.sap_context else None,
            project_id=req.project_id, user_id=user.id, client_id=client_id,
            full_delivery=req.full_delivery,
        )
    except AIDisabledError as e:
        raise HTTPException(status_code=503, detail=str(e))

    if not (req.save and req.project_id):
        return out

    # Persistir el código como artefacto versionable
    if out.get("code"):
        gen = Generation(
            project_id=req.project_id, created_by=user.id,
            agent_key=out.get("agent_key") or out.get("solution_type"),
            provider="-", model="-", sap_context=out.get("sap_context", {}),
            prompt=req.requirement_text[:4000], status="ok",
        )
        db.add(gen)
        db.flush()
        art = CodeArtifact(
            project_id=req.project_id, generation_id=gen.id, created_by=user.id,
            name=out.get("object_name") or "SOLUCION",
            dev_type=out.get("sap_context", {}).get("dev_type"),
            language=out.get("language") or "abap_oo", code=out["code"],
            explanation=out.get("explanation"),
            quality_score=(out.get("lint") or {}).get("score"),
            lint_findings=(out.get("lint") or {}).get("findings", []),
            confidence_notes=out.get("confidence_notes", []), status="generated",
        )
        db.add(art)
        db.flush()
        out["artifact_id"] = art.id

        # Entrega completa: persistir spec, pruebas y documento técnico
        spec = out.get("spec")
        if spec:
            ts = TechSpec(
                requirement_id=None, project_id=req.project_id, created_by=user.id,
                functional_description=spec.get("functional_description"),
                technical_objective=spec.get("technical_objective"),
                assumptions=spec.get("assumptions", []), sap_objects=spec.get("sap_objects", []),
                standard_tables=spec.get("standard_tables", []), suggested_bapis=spec.get("suggested_bapis", []),
                badis_user_exits=spec.get("badis_user_exits", []), risks=spec.get("risks", []),
                dependencies=spec.get("dependencies", []), performance_notes=spec.get("performance_notes"),
                security_notes=spec.get("security_notes"), transport_plan=spec.get("transport_plan"),
                rollback_plan=spec.get("rollback_plan"), raw_markdown=spec.get("raw_markdown"),
            )
            db.add(ts); db.flush(); out["spec_id"] = ts.id
        tests = out.get("tests")
        if tests:
            tsuite = TestSuite(
                project_id=req.project_id, code_artifact_id=art.id, created_by=user.id,
                test_code=tests.get("test_code"), cases=tests.get("cases", []),
                mocks=tests.get("mocks", []), expected_coverage=tests.get("expected_coverage"),
                test_data=tests.get("test_data", []), execution_protocol=tests.get("execution_protocol"),
            )
            db.add(tsuite); db.flush(); out["test_suite_id"] = tsuite.id
        doc = out.get("dev_doc")
        if doc:
            dd = DevDocument(
                project_id=req.project_id, created_by=user.id,
                title=doc.get("title") or "Documento técnico", summary=doc.get("summary"),
                objects=doc.get("objects", []), steps=doc.get("steps", []),
                transport_plan=doc.get("transport_plan"), rollback_plan=doc.get("rollback_plan"),
            )
            db.add(dd); db.flush(); out["dev_doc_id"] = dd.id

        db.commit()
    return out
