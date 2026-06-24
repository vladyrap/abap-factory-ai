from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.permissions import PERMISSIONS, ALL_KEYS
from app.models.user import User
from app.models.role import Role
from app.api.deps import require_perm, get_current_user

router = APIRouter(prefix="/roles", tags=["Roles (RBAC dinámico)"])

require_roles_admin = require_perm("roles.manage")


class RoleCreate(BaseModel):
    name: str
    description: Optional[str] = None
    permissions: list[str] = []


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    permissions: Optional[list[str]] = None


def _clean(perms: list[str]) -> list[str]:
    """Solo permite claves válidas o el comodín '*'."""
    valid = set(ALL_KEYS) | {"*"}
    return [p for p in (perms or []) if p in valid]


@router.get("/permissions", dependencies=[Depends(get_current_user)])
def list_permissions():
    """Catálogo de permisos granulares, agrupados para la UI."""
    groups: dict[str, list] = {}
    for p in PERMISSIONS:
        groups.setdefault(p["group"], []).append({"key": p["key"], "label": p["label"]})
    return {"groups": groups, "all_keys": ALL_KEYS}


@router.get("/", dependencies=[Depends(get_current_user)])
def list_roles(db: Session = Depends(get_db)):
    rows = db.query(Role).order_by(Role.is_system.desc(), Role.name).all()
    return [{"id": r.id, "name": r.name, "description": r.description,
             "is_system": r.is_system, "permissions": r.permissions or []} for r in rows]


@router.post("/", status_code=201, dependencies=[Depends(require_roles_admin)])
def create_role(data: RoleCreate, db: Session = Depends(get_db)):
    if db.query(Role).filter(Role.name == data.name).first():
        raise HTTPException(status_code=400, detail="Ya existe un rol con ese nombre")
    role = Role(name=data.name, description=data.description,
                permissions=_clean(data.permissions), is_system=False)
    db.add(role)
    db.commit()
    db.refresh(role)
    return {"id": role.id}


@router.patch("/{role_id}", dependencies=[Depends(require_roles_admin)])
def update_role(role_id: int, data: RoleUpdate, db: Session = Depends(get_db)):
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    if role.is_system and data.name and data.name != role.name:
        raise HTTPException(status_code=400, detail="No se puede renombrar un rol del sistema")
    if data.name is not None:
        role.name = data.name
    if data.description is not None:
        role.description = data.description
    if data.permissions is not None:
        role.permissions = _clean(data.permissions)
    db.commit()
    return {"ok": True}


@router.delete("/{role_id}", dependencies=[Depends(require_roles_admin)])
def delete_role(role_id: int, db: Session = Depends(get_db)):
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    if role.is_system:
        raise HTTPException(status_code=400, detail="No se puede eliminar un rol del sistema")
    in_use = db.query(User).filter(User.role_id == role_id).count()
    if in_use:
        raise HTTPException(status_code=400, detail=f"El rol está asignado a {in_use} usuario(s)")
    db.delete(role)
    db.commit()
    return {"ok": True}
