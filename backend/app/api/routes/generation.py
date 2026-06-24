from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.generation import Generation
from app.models.code_artifact import CodeArtifact
from app.schemas.workbench import (
    GenerateRequest, GenerateResponse, CodeArtifactResponse, EditorRequest, SpecRequest,
    ArtifactUpdate,
)
from app.api.deps import get_current_user, require_builder, require_approver
from app.services.ai import generator, editor, spec_gen
from app.services.ai.engine import AIDisabledError
from app.services.ai import pricing

router = APIRouter(prefix="/generation", tags=["Generación ABAP"])


def _guard(fn, *a, **k):
    try:
        return fn(*a, **k)
    except AIDisabledError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.post("/code", response_model=GenerateResponse)
def generate(req: GenerateRequest, db: Session = Depends(get_db), user: User = Depends(require_builder)):
    ctx = req.sap_context.model_dump()
    out = _guard(
        generator.generate_code, db,
        description=req.description, sap_context=ctx,
        project_id=req.project_id, user_id=user.id, agent_override=req.agent_override,
    )

    artifact = None
    if req.save and req.project_id:
        gen = Generation(
            project_id=req.project_id, requirement_id=req.requirement_id, created_by=user.id,
            agent_key=out["agent_key"], provider=out["provider"], model=out["model"],
            sap_context=ctx, prompt=req.description, status="ok",
            tokens_in=out["tokens_in"], tokens_out=out["tokens_out"],
            cost_usd=pricing.cost_usd(out["model"], out["tokens_in"], out["tokens_out"]),
            latency_ms=out["latency_ms"],
        )
        db.add(gen)
        db.flush()
        artifact = CodeArtifact(
            project_id=req.project_id, requirement_id=req.requirement_id, generation_id=gen.id,
            created_by=user.id, name=out["object_name"], dev_type=ctx.get("dev_type"),
            language=out["language"], code=out["code"], explanation=out["explanation"],
        )
        db.add(artifact)
        db.commit()
        db.refresh(artifact)

    return GenerateResponse(
        artifact=CodeArtifactResponse.model_validate(artifact) if artifact else None,
        object_name=out["object_name"], language=out["language"], code=out["code"],
        explanation=out["explanation"], agent_key=out["agent_key"],
        provider=out["provider"], model=out["model"],
    )


@router.post("/editor")
def editor_op(req: EditorRequest, db: Session = Depends(get_db), user: User = Depends(require_builder)):
    return _guard(
        editor.run_editor_op, db,
        operation=req.operation, source_code=req.source_code,
        project_id=req.project_id, user_id=user.id,
    )


@router.post("/spec")
def generate_spec(req: SpecRequest, db: Session = Depends(get_db), user: User = Depends(require_builder)):
    from app.models.tech_spec import TechSpec
    out = _guard(
        spec_gen.generate_spec, db,
        description=req.description, sap_context=req.sap_context.model_dump(),
        project_id=req.project_id, user_id=user.id,
    )
    if req.save and req.requirement_id:
        spec = TechSpec(
            requirement_id=req.requirement_id, project_id=req.project_id, created_by=user.id,
            functional_description=out.get("functional_description"),
            technical_objective=out.get("technical_objective"),
            assumptions=out.get("assumptions", []), sap_objects=out.get("sap_objects", []),
            standard_tables=out.get("standard_tables", []), suggested_bapis=out.get("suggested_bapis", []),
            badis_user_exits=out.get("badis_user_exits", []), risks=out.get("risks", []),
            dependencies=out.get("dependencies", []), performance_notes=out.get("performance_notes"),
            security_notes=out.get("security_notes"), transport_plan=out.get("transport_plan"),
            rollback_plan=out.get("rollback_plan"), raw_markdown=out.get("raw_markdown"),
        )
        db.add(spec)
        db.commit()
        db.refresh(spec)
        out["id"] = spec.id
    return out


# ─── Historial / artefactos ──────────────────────────────────────────────────
@router.get("/artifacts", response_model=list[CodeArtifactResponse], dependencies=[Depends(get_current_user)])
def list_artifacts(project_id: int | None = None, db: Session = Depends(get_db)):
    q = db.query(CodeArtifact)
    if project_id:
        q = q.filter(CodeArtifact.project_id == project_id)
    return q.order_by(CodeArtifact.created_at.desc()).limit(200).all()


@router.get("/artifacts/{artifact_id}", response_model=CodeArtifactResponse,
            dependencies=[Depends(get_current_user)])
def get_artifact(artifact_id: int, db: Session = Depends(get_db)):
    art = db.query(CodeArtifact).filter(CodeArtifact.id == artifact_id).first()
    if not art:
        raise HTTPException(status_code=404, detail="Artefacto no encontrado")
    return art


def _root_id(db: Session, art: CodeArtifact) -> int:
    """Devuelve el id raíz de la cadena de versiones."""
    current = art
    while current.parent_id:
        parent = db.query(CodeArtifact).filter(CodeArtifact.id == current.parent_id).first()
        if not parent:
            break
        current = parent
    return current.id


@router.get("/artifacts/{artifact_id}/versions", response_model=list[CodeArtifactResponse],
            dependencies=[Depends(get_current_user)])
def list_versions(artifact_id: int, db: Session = Depends(get_db)):
    """Cadena de versiones (toda la familia que comparte la misma raíz)."""
    art = db.query(CodeArtifact).filter(CodeArtifact.id == artifact_id).first()
    if not art:
        raise HTTPException(status_code=404, detail="Artefacto no encontrado")
    root = _root_id(db, art)
    family, seen = [], set()
    frontier = [root]
    while frontier:
        cur = frontier.pop()
        if cur in seen:
            continue
        seen.add(cur)
        node = db.query(CodeArtifact).filter(CodeArtifact.id == cur).first()
        if node:
            family.append(node)
            children = db.query(CodeArtifact).filter(CodeArtifact.parent_id == cur).all()
            frontier.extend(c.id for c in children)
    return sorted(family, key=lambda a: a.version)


@router.patch("/artifacts/{artifact_id}", response_model=CodeArtifactResponse)
def edit_artifact(artifact_id: int, data: ArtifactUpdate, db: Session = Depends(get_db),
                  user: User = Depends(require_builder)):
    """Edita el código creando una NUEVA versión encadenada (no muta la anterior)."""
    art = db.query(CodeArtifact).filter(CodeArtifact.id == artifact_id).first()
    if not art:
        raise HTTPException(status_code=404, detail="Artefacto no encontrado")
    new_art = CodeArtifact(
        project_id=art.project_id, requirement_id=art.requirement_id,
        generation_id=art.generation_id, created_by=user.id,
        name=data.name or art.name, dev_type=art.dev_type, language=art.language,
        code=data.code if data.code is not None else art.code,
        explanation=data.explanation if data.explanation is not None else art.explanation,
        version=(art.version or 1) + 1, parent_id=art.id, status="edited",
    )
    db.add(new_art)
    db.commit()
    db.refresh(new_art)
    return new_art


@router.post("/artifacts/{artifact_id}/approve", response_model=CodeArtifactResponse)
def approve_artifact(artifact_id: int, db: Session = Depends(get_db),
                     user: User = Depends(require_approver)):
    """Aprueba un artefacto (solo admin / líder técnico)."""
    art = db.query(CodeArtifact).filter(CodeArtifact.id == artifact_id).first()
    if not art:
        raise HTTPException(status_code=404, detail="Artefacto no encontrado")
    art.status = "approved"
    db.commit()
    db.refresh(art)
    return art
