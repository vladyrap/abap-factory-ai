from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.core import ratelimit
from app.core.security import (
    verify_password, get_password_hash, create_access_token, create_refresh_token, decode_token,
)
from app.models.user import User, UserRole
from app.schemas.user import (
    UserCreate, UserResponse, Token, LoginRequest, RefreshRequest, TwoFAVerify,
)
from app.api.deps import get_current_user, require_admin, effective_permissions

router = APIRouter(prefix="/auth", tags=["Autenticación"])


def _with_perms(db: Session, user: User) -> User:
    user.permissions = sorted(effective_permissions(db, user))
    return user


def _tokens(user: User) -> dict:
    claims = {"sub": str(user.id), "role": user.role.value, "tv": user.token_version or 1}
    return {"access_token": create_access_token(claims), "refresh_token": create_refresh_token(claims)}


def _verify_totp(secret: str, otp: str) -> bool:
    try:
        import pyotp
        return pyotp.TOTP(secret).verify(otp or "", valid_window=1)
    except Exception:  # noqa: BLE001
        return False


@router.post("/login", response_model=Token)
def login(credentials: LoginRequest, request: Request, db: Session = Depends(get_db)):
    # Rate limiting anti fuerza bruta (por IP + email)
    ip = request.client.host if request.client else "?"
    rl_key = f"login:{ip}:{credentials.email.lower()}"
    if not ratelimit.check_and_hit(rl_key, settings.LOGIN_RATE_MAX, settings.LOGIN_RATE_WINDOW_SEC):
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                            detail="Demasiados intentos de inicio de sesión. Espera unos minutos.")

    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cuenta desactivada")
    # 2FA
    if user.totp_enabled:
        if not credentials.otp:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="otp_required")
        if not _verify_totp(user.totp_secret, credentials.otp):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="otp_invalid")

    ratelimit.reset(rl_key)  # login correcto: limpia el contador
    t = _tokens(user)
    return Token(access_token=t["access_token"], refresh_token=t["refresh_token"], user=_with_perms(db, user))


@router.post("/refresh", response_model=Token)
def refresh(data: RefreshRequest, db: Session = Depends(get_db)):
    payload = decode_token(data.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token inválido")
    user = db.query(User).filter(User.id == payload.get("sub")).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no encontrado")
    tv = payload.get("tv")
    if tv is not None and tv != (user.token_version or 1):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sesión expirada")
    t = _tokens(user)
    return Token(access_token=t["access_token"], refresh_token=t["refresh_token"], user=_with_perms(db, user))


@router.post("/logout-all")
def logout_all(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Invalida todas las sesiones del usuario (sube su token_version)."""
    current_user.token_version = (current_user.token_version or 1) + 1
    db.commit()
    return {"ok": True}


@router.get("/me", response_model=UserResponse)
def get_me(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return _with_perms(db, current_user)


@router.post("/users", response_model=UserResponse, status_code=201, dependencies=[Depends(require_admin)])
def create_user(data: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    user = User(
        email=data.email, password_hash=get_password_hash(data.password),
        first_name=data.first_name, last_name=data.last_name, role=data.role or UserRole.consultant,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# ─── 2FA (TOTP) — el usuario gestiona su propio segundo factor ───────────────
@router.get("/2fa/status")
def twofa_status(current_user: User = Depends(get_current_user)):
    return {"enabled": bool(current_user.totp_enabled)}


@router.post("/2fa/setup")
def twofa_setup(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Genera un secreto y devuelve el URI otpauth + QR (SVG) para escanear."""
    import pyotp
    secret = pyotp.random_base32()
    current_user.totp_secret = secret
    current_user.totp_enabled = False
    db.commit()
    uri = pyotp.totp.TOTP(secret).provisioning_uri(name=current_user.email, issuer_name=settings.TOTP_ISSUER)
    qr_svg = ""
    try:
        import qrcode
        import qrcode.image.svg
        img = qrcode.make(uri, image_factory=qrcode.image.svg.SvgImage)
        import io
        buf = io.BytesIO()
        img.save(buf)
        qr_svg = buf.getvalue().decode("utf-8")
    except Exception:  # noqa: BLE001 — si falta qrcode, igual devolvemos secret+uri
        pass
    return {"secret": secret, "otpauth_uri": uri, "qr_svg": qr_svg}


@router.post("/2fa/enable")
def twofa_enable(data: TwoFAVerify, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.totp_secret:
        raise HTTPException(status_code=400, detail="Primero ejecuta el setup de 2FA")
    if not _verify_totp(current_user.totp_secret, data.otp):
        raise HTTPException(status_code=400, detail="Código inválido")
    current_user.totp_enabled = True
    db.commit()
    return {"enabled": True}


@router.post("/2fa/disable")
def twofa_disable(data: TwoFAVerify, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.totp_enabled and not _verify_totp(current_user.totp_secret, data.otp):
        raise HTTPException(status_code=400, detail="Código inválido")
    current_user.totp_enabled = False
    current_user.totp_secret = None
    db.commit()
    return {"enabled": False}
