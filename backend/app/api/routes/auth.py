from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserResponse, Token, LoginRequest
from app.api.deps import get_current_user, require_admin

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/login", response_model=Token)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cuenta desactivada")
    token = create_access_token({"sub": str(user.id), "role": user.role.value})
    return Token(access_token=token, user=user)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/users", response_model=UserResponse, status_code=201, dependencies=[Depends(require_admin)])
def create_user(data: UserCreate, db: Session = Depends(get_db)):
    """Solo admin crea usuarios (no hay auto-registro en una herramienta interna)."""
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    user = User(
        email=data.email,
        password_hash=get_password_hash(data.password),
        first_name=data.first_name,
        last_name=data.last_name,
        role=data.role or UserRole.consultant,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
