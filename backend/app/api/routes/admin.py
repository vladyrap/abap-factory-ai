from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_password_hash
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate
from app.api.deps import require_admin

router = APIRouter(prefix="/admin", tags=["Administración"], dependencies=[Depends(require_admin)])


@router.get("/users", response_model=list[UserResponse])
def list_users(db: Session = Depends(get_db)):
    return db.query(User).order_by(User.created_at.desc()).all()


@router.patch("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, data: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    payload = data.model_dump(exclude_none=True)
    if "password" in payload:
        user.password_hash = get_password_hash(payload.pop("password"))
        user.token_version = (user.token_version or 1) + 1  # invalida sesiones previas
    for k, v in payload.items():
        setattr(user, k, v)
    db.commit()
    db.refresh(user)
    return user


@router.put("/users/{user_id}/toggle-active", response_model=UserResponse)
def toggle_active(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    user.is_active = not user.is_active
    db.commit()
    db.refresh(user)
    return user
