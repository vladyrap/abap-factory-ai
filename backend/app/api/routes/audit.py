from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.audit_log import AuditLog
from app.api.deps import require_perm

router = APIRouter(prefix="/audit", tags=["Auditoría"])


@router.get("/", dependencies=[Depends(require_perm("audit.view"))])
def list_audit(limit: int = 200, user_id: int | None = None, db: Session = Depends(get_db)):
    q = db.query(AuditLog)
    if user_id:
        q = q.filter(AuditLog.user_id == user_id)
    rows = q.order_by(AuditLog.created_at.desc()).limit(min(limit, 1000)).all()
    return [
        {"id": r.id, "user_email": r.user_email, "action": r.action, "method": r.method,
         "path": r.path, "status": r.status, "ip": r.ip, "created_at": r.created_at}
        for r in rows
    ]
