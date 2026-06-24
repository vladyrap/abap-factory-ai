from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import decode_token
from app.core.permissions import LEGACY_ROLE_PERMS, has_perm
from app.models.user import User, UserRole
from app.models.role import Role

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido o expirado")
    user = db.query(User).filter(User.id == payload.get("sub")).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no encontrado")
    return user


def effective_permissions(db: Session, user: User) -> set[str]:
    """Permisos efectivos: rol dinámico (role_id) si existe, si no el rol legado."""
    if user.role_id:
        role = db.query(Role).filter(Role.id == user.role_id).first()
        if role:
            return set(role.permissions or [])
    legacy = user.role.value if hasattr(user.role, "value") else (user.role or "consultant")
    return set(LEGACY_ROLE_PERMS.get(legacy, []))


def require_perm(*keys: str):
    """Exige que el usuario tenga al menos uno de los permisos indicados."""
    def checker(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> User:
        perms = effective_permissions(db, current_user)
        if not any(has_perm(perms, k) for k in keys):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sin permisos suficientes")
        return current_user
    return checker


# ─── Compatibilidad: los deps existentes ahora se respaldan en permisos ──────
require_admin = require_perm("users.manage")
require_builder = require_perm("code.generate")
require_approver = require_perm("code.approve")
require_qa = require_perm("tests.generate")


# Compatibilidad con código que aún use require_role(UserRole...)
def require_role(*roles: UserRole):
    def checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sin permisos suficientes")
        return current_user
    return checker
