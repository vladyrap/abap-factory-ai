from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.sap_connection import SapConnection
from app.schemas.workbench import SapConnectionUpdate
from app.api.deps import get_current_user, require_builder

router = APIRouter(prefix="/connections", tags=["Conexión SAP / abapGit"])


@router.get("/project/{project_id}", dependencies=[Depends(get_current_user)])
def get_connection(project_id: int, db: Session = Depends(get_db)):
    conn = db.query(SapConnection).filter(SapConnection.project_id == project_id).first()
    if not conn:
        return {"project_id": project_id, "kind": "abapgit", "branch": "main"}
    return {c.name: getattr(conn, c.name) for c in conn.__table__.columns}


@router.put("/project/{project_id}")
def set_connection(project_id: int, data: SapConnectionUpdate, db: Session = Depends(get_db),
                   _: User = Depends(require_builder)):
    conn = db.query(SapConnection).filter(SapConnection.project_id == project_id).first()
    if not conn:
        conn = SapConnection(project_id=project_id)
        db.add(conn)
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(conn, k, v)
    db.commit()
    return {"ok": True}
