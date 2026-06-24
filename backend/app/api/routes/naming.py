from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.naming_rule import NamingRule, NAMING_OBJECT_TYPES
from app.schemas.workbench import NamingRuleCreate, NamingPreviewRequest
from app.api.deps import get_current_user, require_builder
from app.services import naming

router = APIRouter(prefix="/naming", tags=["Nomenclaturas dinámicas"])


@router.get("/object-types", dependencies=[Depends(get_current_user)])
def object_types():
    return list(NAMING_OBJECT_TYPES)


@router.get("/client/{client_id}", dependencies=[Depends(get_current_user)])
def list_rules(client_id: int, db: Session = Depends(get_db)):
    rows = naming.get_rules(db, client_id)
    return [{"id": r.id, "object_type": r.object_type, "pattern": r.pattern,
             "example": r.example, "description": r.description,
             "placeholders": naming.placeholders(r.pattern)} for r in rows]


@router.post("/", status_code=201)
def create_rule(data: NamingRuleCreate, db: Session = Depends(get_db), user: User = Depends(require_builder)):
    if data.object_type not in NAMING_OBJECT_TYPES:
        raise HTTPException(status_code=400, detail="Tipo de objeto no soportado")
    # upsert por (client, object_type)
    rule = (
        db.query(NamingRule)
        .filter(NamingRule.client_id == data.client_id, NamingRule.object_type == data.object_type)
        .first()
    )
    if not rule:
        rule = NamingRule(client_id=data.client_id, object_type=data.object_type, created_by=user.id)
        db.add(rule)
    rule.pattern = data.pattern
    rule.example = data.example or naming.apply_pattern(data.pattern, {"MODULE": "FI", "AREA": "FI", "NAME": "EJEMPLO"})
    rule.description = data.description
    db.commit()
    db.refresh(rule)
    return {"id": rule.id, "example": rule.example}


@router.post("/preview", dependencies=[Depends(get_current_user)])
def preview(req: NamingPreviewRequest):
    return {"name": naming.apply_pattern(req.pattern, req.variables),
            "placeholders": naming.placeholders(req.pattern)}


@router.delete("/{rule_id}", dependencies=[Depends(require_builder)])
def delete_rule(rule_id: int, db: Session = Depends(get_db)):
    rule = db.query(NamingRule).filter(NamingRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="No encontrada")
    db.delete(rule)
    db.commit()
    return {"ok": True}
