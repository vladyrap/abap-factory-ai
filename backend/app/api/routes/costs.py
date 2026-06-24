from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user, require_approver
from app.models.user import User
from app.models.ai_usage import AIUsage
from app.models.project import Project

router = APIRouter(prefix="/costs", tags=["Costos IA"])


@router.get("/summary", dependencies=[Depends(require_approver)])
def summary(db: Session = Depends(get_db)):
    total_usd, total_clp, total_in, total_out, calls = db.query(
        func.sum(AIUsage.cost_usd), func.sum(AIUsage.cost_clp),
        func.sum(AIUsage.tokens_in), func.sum(AIUsage.tokens_out), func.count(AIUsage.id),
    ).first()

    by_provider = db.query(
        AIUsage.provider, func.count(AIUsage.id), func.sum(AIUsage.cost_usd)
    ).group_by(AIUsage.provider).all()

    by_operation = db.query(
        AIUsage.operation, func.count(AIUsage.id), func.sum(AIUsage.cost_usd)
    ).group_by(AIUsage.operation).all()

    by_user = db.query(
        User.email, func.count(AIUsage.id), func.sum(AIUsage.cost_usd)
    ).join(User, User.id == AIUsage.user_id).group_by(User.email).all()

    by_project = db.query(
        Project.name, func.count(AIUsage.id), func.sum(AIUsage.cost_usd)
    ).join(Project, Project.id == AIUsage.project_id).group_by(Project.name).all()

    return {
        "total_usd": round(total_usd or 0, 4),
        "total_clp": round(total_clp or 0, 0),
        "total_tokens_in": total_in or 0,
        "total_tokens_out": total_out or 0,
        "total_calls": calls or 0,
        "by_provider": [{"provider": p, "calls": c, "usd": round(u or 0, 4)} for p, c, u in by_provider],
        "by_operation": [{"operation": o, "calls": c, "usd": round(u or 0, 4)} for o, c, u in by_operation],
        "by_user": [{"user": e, "calls": c, "usd": round(u or 0, 4)} for e, c, u in by_user],
        "by_project": [{"project": n, "calls": c, "usd": round(u or 0, 4)} for n, c, u in by_project],
    }


@router.get("/history", dependencies=[Depends(get_current_user)])
def history(limit: int = 100, db: Session = Depends(get_db)):
    rows = db.query(AIUsage).order_by(AIUsage.created_at.desc()).limit(min(limit, 500)).all()
    return [
        {"id": r.id, "operation": r.operation, "agent_key": r.agent_key, "provider": r.provider,
         "model": r.model, "tokens_in": r.tokens_in, "tokens_out": r.tokens_out,
         "cost_usd": r.cost_usd, "cost_clp": r.cost_clp, "created_at": r.created_at}
        for r in rows
    ]
