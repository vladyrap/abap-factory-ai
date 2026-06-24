from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.generation import Generation
from app.models.code_artifact import CodeArtifact
from app.schemas.workbench import SolutionRequest
from app.api.deps import get_current_user, require_builder
from app.services.ai import solution
from app.services.ai.engine import AIDisabledError
from app.services.ai import pricing

router = APIRouter(prefix="/solution", tags=["Requerimiento → Solución"])


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
        )
    except AIDisabledError as e:
        raise HTTPException(status_code=503, detail=str(e))

    # Persistir el código resultante como artefacto del proyecto (versionable)
    if req.save and req.project_id and out.get("code"):
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
            confidence_notes=out.get("confidence_notes", []),
            status="generated",
        )
        db.add(art)
        db.commit()
        db.refresh(art)
        out["artifact_id"] = art.id
    return out
