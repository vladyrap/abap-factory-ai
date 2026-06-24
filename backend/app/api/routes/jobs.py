from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user, require_builder
from app.models.user import User
from app.models.job import Job, JOB_TYPES
from app.services import scheduler

router = APIRouter(prefix="/jobs", tags=["Procesos asíncronos"])


class JobCreate(BaseModel):
    project_id: int
    job_type: str          # batch_inspect | batch_generate
    params: dict = {}


@router.post("/", status_code=201)
def create_job(data: JobCreate, db: Session = Depends(get_db), user: User = Depends(require_builder)):
    if data.job_type not in JOB_TYPES:
        raise HTTPException(status_code=400, detail=f"Tipo inválido. Use: {', '.join(JOB_TYPES)}")
    job = Job(project_id=data.project_id, created_by=user.id, job_type=data.job_type, params=data.params)
    db.add(job)
    db.commit()
    db.refresh(job)
    scheduler.enqueue(job.id)
    return {"id": job.id, "status": job.status}


@router.get("/", dependencies=[Depends(get_current_user)])
def list_jobs(project_id: int | None = None, db: Session = Depends(get_db)):
    q = db.query(Job)
    if project_id:
        q = q.filter(Job.project_id == project_id)
    rows = q.order_by(Job.created_at.desc()).limit(100).all()
    return [_serialize(j) for j in rows]


@router.get("/{job_id}", dependencies=[Depends(get_current_user)])
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job no encontrado")
    return _serialize(job)


def _serialize(j: Job) -> dict:
    return {
        "id": j.id, "project_id": j.project_id, "job_type": j.job_type, "status": j.status,
        "total": j.total, "processed": j.processed, "result": j.result, "error": j.error,
        "created_at": j.created_at, "finished_at": j.finished_at,
    }
