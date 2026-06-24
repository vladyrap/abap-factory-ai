from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.project import Project
from app.models.requirement import Requirement
from app.schemas.catalog import ProjectCreate, ProjectUpdate, ProjectResponse
from app.schemas.workbench import RequirementCreate, RequirementResponse
from app.api.deps import get_current_user, require_builder
from app.models.user import User

router = APIRouter(prefix="/projects", tags=["Proyectos"])


@router.get("/", response_model=list[ProjectResponse], dependencies=[Depends(get_current_user)])
def list_projects(client_id: int | None = None, db: Session = Depends(get_db)):
    q = db.query(Project)
    if client_id:
        q = q.filter(Project.client_id == client_id)
    return q.order_by(Project.created_at.desc()).all()


@router.get("/{project_id}", response_model=ProjectResponse, dependencies=[Depends(get_current_user)])
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return project


@router.post("/", response_model=ProjectResponse, status_code=201)
def create_project(data: ProjectCreate, db: Session = Depends(get_db), user: User = Depends(require_builder)):
    project = Project(**data.model_dump(), owner_user_id=user.id)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.patch("/{project_id}", response_model=ProjectResponse, dependencies=[Depends(require_builder)])
def update_project(project_id: int, data: ProjectUpdate, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(project, k, v)
    db.commit()
    db.refresh(project)
    return project


# ─── Requerimientos del proyecto ─────────────────────────────────────────────
@router.get("/{project_id}/requirements", response_model=list[RequirementResponse],
            dependencies=[Depends(get_current_user)])
def list_requirements(project_id: int, db: Session = Depends(get_db)):
    return (
        db.query(Requirement)
        .filter(Requirement.project_id == project_id)
        .order_by(Requirement.created_at.desc())
        .all()
    )


@router.post("/requirements", response_model=RequirementResponse, status_code=201)
def create_requirement(data: RequirementCreate, db: Session = Depends(get_db), user: User = Depends(require_builder)):
    req = Requirement(**data.model_dump(), created_by=user.id)
    db.add(req)
    db.commit()
    db.refresh(req)
    return req
