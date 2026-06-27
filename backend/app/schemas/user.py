from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from app.models.user import UserRole


class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str


class UserCreate(UserBase):
    password: str = Field(min_length=8)   # política mínima de contraseña
    role: UserRole = UserRole.consultant


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[UserRole] = None
    role_id: Optional[int] = None
    is_active: Optional[bool] = None
    password: Optional[str] = Field(default=None, min_length=8)


class UserResponse(UserBase):
    id: int
    role: UserRole
    role_id: Optional[int] = None
    is_active: bool
    created_at: datetime
    permissions: list[str] = []     # permisos efectivos (se completa en login / me)

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    user: UserResponse


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    otp: Optional[str] = None     # código 2FA (TOTP) si el usuario lo tiene activado


class RefreshRequest(BaseModel):
    refresh_token: str


class TwoFAVerify(BaseModel):
    otp: str
