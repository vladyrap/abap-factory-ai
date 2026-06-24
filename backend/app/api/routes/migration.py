from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.migration import Migration
from app.schemas.workbench import MigrateRequest
from app.api.deps import get_current_user, require_builder
from app.services.ai import migrator
from app.services.ai.engine import AIDisabledError

router = APIRouter(prefix="/migration", tags=["Migración ECC → S/4"])


@router.post("/migrate")
def migrate(req: MigrateRequest, db: Session = Depends(get_db), user: User = Depends(require_builder)):
    try:
        out = migrator.migrate_code(
            db, source_code=req.source_code, target=req.target,
            project_id=req.project_id, user_id=user.id,
        )
    except AIDisabledError as e:
        raise HTTPException(status_code=503, detail=str(e))

    if req.save:
        rec = Migration(
            project_id=req.project_id, created_by=user.id, source_code=req.source_code,
            target=req.target, migrated_code=out.get("migrated_code"),
            changes=out.get("changes", []), simplification_items=out.get("simplification_items", []),
            compatibility=out.get("compatibility"), notes=out.get("notes"),
            manual_steps=out.get("manual_steps", []),
            provider=out.get("_meta", {}).get("provider"), model=out.get("_meta", {}).get("model"),
        )
        db.add(rec)
        db.commit()
        db.refresh(rec)
        out["id"] = rec.id
    return out


@router.get("/", dependencies=[Depends(get_current_user)])
def list_migrations(project_id: int | None = None, db: Session = Depends(get_db)):
    q = db.query(Migration)
    if project_id:
        q = q.filter(Migration.project_id == project_id)
    rows = q.order_by(Migration.created_at.desc()).limit(100).all()
    return [{"id": r.id, "target": r.target, "compatibility": r.compatibility,
             "changes": len(r.changes or []), "created_at": r.created_at} for r in rows]


@router.get("/{mig_id}", dependencies=[Depends(get_current_user)])
def get_migration(mig_id: int, db: Session = Depends(get_db)):
    r = db.query(Migration).filter(Migration.id == mig_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Migración no encontrada")
    return {c.name: getattr(r, c.name) for c in r.__table__.columns}
