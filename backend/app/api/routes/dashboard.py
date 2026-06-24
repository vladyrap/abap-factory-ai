from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.code_artifact import CodeArtifact
from app.models.dump_analysis import DumpAnalysis
from app.models.code_inspection import CodeInspection
from app.models.test_suite import TestSuite
from app.models.ai_usage import AIUsage

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats")
def stats(project_id: int | None = None, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    def scoped(q, model):
        return q.filter(model.project_id == project_id) if project_id else q

    total_programs = scoped(db.query(func.count(CodeArtifact.id)), CodeArtifact).scalar() or 0
    dumps_resolved = scoped(db.query(func.count(DumpAnalysis.id)), DumpAnalysis).scalar() or 0
    avg_score = scoped(db.query(func.avg(CodeInspection.score)), CodeInspection).scalar()
    findings = scoped(db.query(func.count(CodeInspection.id)), CodeInspection).scalar() or 0
    tests_generated = scoped(db.query(func.count(TestSuite.id)), TestSuite).scalar() or 0

    cost_q = db.query(func.sum(AIUsage.cost_usd), func.sum(AIUsage.cost_clp))
    if project_id:
        cost_q = cost_q.filter(AIUsage.project_id == project_id)
    cost_usd, cost_clp = cost_q.first()

    # Errores de dump más frecuentes
    freq_q = db.query(DumpAnalysis.dump_type, func.count(DumpAnalysis.id).label("n"))
    if project_id:
        freq_q = freq_q.filter(DumpAnalysis.project_id == project_id)
    frequent = (
        freq_q.filter(DumpAnalysis.dump_type.isnot(None))
        .group_by(DumpAnalysis.dump_type).order_by(func.count(DumpAnalysis.id).desc()).limit(5).all()
    )

    # Estimación de tiempo ahorrado: heurística simple por operación
    op_minutes = {"generate": 120, "dump": 45, "inspect": 30, "unit_test": 60, "protocol": 40, "spec": 90}
    usage_counts = db.query(AIUsage.operation, func.count(AIUsage.id))
    if project_id:
        usage_counts = usage_counts.filter(AIUsage.project_id == project_id)
    saved_minutes = sum(op_minutes.get(op, 20) * n for op, n in usage_counts.group_by(AIUsage.operation).all())

    return {
        "total_programs": total_programs,
        "dumps_resolved": dumps_resolved,
        "avg_quality_score": round(avg_score, 1) if avg_score else None,
        "inspector_findings": findings,
        "tests_generated": tests_generated,
        "cost_usd": round(cost_usd or 0, 4),
        "cost_clp": round(cost_clp or 0, 0),
        "frequent_dumps": [{"type": t, "count": n} for t, n in frequent],
        "estimated_hours_saved": round(saved_minutes / 60, 1),
    }


@router.get("/recent")
def recent(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    arts = db.query(CodeArtifact).order_by(CodeArtifact.created_at.desc()).limit(8).all()
    dumps = db.query(DumpAnalysis).order_by(DumpAnalysis.created_at.desc()).limit(8).all()
    return {
        "artifacts": [{"id": a.id, "name": a.name, "dev_type": a.dev_type,
                       "created_at": a.created_at} for a in arts],
        "dumps": [{"id": d.id, "dump_type": d.dump_type, "severity": d.severity,
                   "created_at": d.created_at} for d in dumps],
    }
