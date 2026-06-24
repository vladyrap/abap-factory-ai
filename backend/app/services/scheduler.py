"""Procesos asíncronos con APScheduler.

El scheduler corre en el mismo proceso (BackgroundScheduler). Los jobs ejecutan
trabajos por lote sobre un proyecto: re-inspección masiva o generación masiva.
Cada job abre su propia sesión de BD (no comparte la del request).
"""
from __future__ import annotations
import logging
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler

from app.core.database import SessionLocal
from app.models.job import Job
from app.models.code_artifact import CodeArtifact
from app.models.requirement import Requirement
from app.models.project import Project
from app.services.ai import inspector, generator
from app.services.ai.engine import AIDisabledError

logger = logging.getLogger(__name__)
scheduler = BackgroundScheduler(daemon=True)


def start():
    if not scheduler.running:
        scheduler.start()
        logger.info("scheduler.started")


def enqueue(job_id: int):
    """Programa la ejecución inmediata de un job en background."""
    scheduler.add_job(_run, args=[job_id], id=f"job-{job_id}", replace_existing=True)


def _run(job_id: int):
    db = SessionLocal()
    job = None
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return
        job.status = "running"
        job.started_at = datetime.utcnow()
        db.commit()

        if job.job_type == "batch_inspect":
            _batch_inspect(db, job)
        elif job.job_type == "batch_generate":
            _batch_generate(db, job)
        else:
            raise ValueError(f"Tipo de job desconocido: {job.job_type}")

        job.status = "done"
    except AIDisabledError as e:
        job.status = "error"
        job.error = str(e)
    except Exception as e:  # noqa: BLE001
        logger.exception("scheduler.job_failed")
        job.status = "error"
        job.error = str(e)
    finally:
        if job is not None:
            job.finished_at = datetime.utcnow()
            db.commit()
        db.close()


def _batch_inspect(db, job: Job):
    """Re-inspecciona todos los artefactos del proyecto y guarda resultados."""
    from app.models.code_inspection import CodeInspection
    arts = db.query(CodeArtifact).filter(CodeArtifact.project_id == job.project_id).all()
    job.total = len(arts)
    db.commit()
    scores = []
    for art in arts:
        out = inspector.inspect_code(
            db, source_code=art.code, project_id=job.project_id, user_id=job.created_by,
        )
        rec = CodeInspection(
            project_id=job.project_id, code_artifact_id=art.id, created_by=job.created_by,
            source_code=art.code, score=out.get("score", 0),
            s4hana_compatible=out.get("s4hana_compatible"), findings=out.get("findings", []),
            rules_violated=out.get("rules_violated", []), recommendation=out.get("recommendation"),
            corrected_code=out.get("corrected_code"),
            provider=out.get("_meta", {}).get("provider"), model=out.get("_meta", {}).get("model"),
        )
        db.add(rec)
        scores.append(out.get("score", 0))
        job.processed += 1
        db.commit()
    job.result = {"avg_score": round(sum(scores) / len(scores), 1) if scores else None,
                  "inspected": len(arts)}


def _batch_generate(db, job: Job):
    """Genera código para todos los requerimientos en estado 'draft' del proyecto."""
    reqs = (
        db.query(Requirement)
        .filter(Requirement.project_id == job.project_id, Requirement.status == "draft")
        .all()
    )
    job.total = len(reqs)
    db.commit()
    project = db.query(Project).filter(Project.id == job.project_id).first()
    generated = []
    for req in reqs:
        ctx = {"sap_version": req.sap_version, "module": req.module, "dev_type": req.dev_type,
               "complexity": req.complexity, "naming_convention": req.naming_convention}
        out = generator.generate_code(
            db, description=req.description or req.title, sap_context=ctx,
            project_id=job.project_id, user_id=job.created_by,
        )
        art = CodeArtifact(
            project_id=job.project_id, requirement_id=req.id, created_by=job.created_by,
            name=out["object_name"], dev_type=req.dev_type, language=out["language"],
            code=out["code"], explanation=out["explanation"],
        )
        db.add(art)
        req.status = "generated"
        generated.append(out["object_name"])
        job.processed += 1
        db.commit()
    job.result = {"generated": generated}
