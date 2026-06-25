from __future__ import annotations
from pydantic_settings import BaseSettings
from typing import Optional, List


class Settings(BaseSettings):
    PROJECT_NAME: str = "ABAP Factory AI"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"

    SECRET_KEY: str = "change-me-in-production-use-a-long-random-string"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 8        # 8h — token de acceso (corto)
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 14  # 14 días — token de refresh
    TOTP_ISSUER: str = "ABAP Factory AI"             # nombre que ve el authenticator (2FA)

    # PostgreSQL — puertos propios para no chocar con otros proyectos locales
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "abap_factory"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 6602

    # Override directo de la URL (p.ej. para desarrollo local con SQLite sin Docker:
    # DATABASE_URL_OVERRIDE=sqlite:///./dev.db). Si está vacío, se arma desde POSTGRES_*.
    DATABASE_URL_OVERRIDE: Optional[str] = None

    CORS_ORIGINS: List[str] = ["http://localhost:6600", "http://localhost:5173"]

    LOG_LEVEL: str = "INFO"
    APP_PUBLIC_URL: str = "http://localhost:6600"
    ENV: str = "dev"   # dev | prod — en prod se valida SECRET_KEY

    # ─── Robustez ───────────────────────────────────────────────────────────
    AI_TIMEOUT_SECONDS: int = 90        # timeout por llamada a la IA
    AI_MAX_RETRIES: int = 2             # reintentos ante errores transitorios
    MAX_INPUT_CHARS: int = 60000        # tope de tamaño de código/dump pegado
    DAILY_AI_COST_LIMIT_USD: float = 0  # 0 = sin límite; si >0, corta al superarlo por usuario/día

    # Rate limiting del login (anti fuerza bruta) — por IP+email
    LOGIN_RATE_MAX: int = 10            # intentos fallidos permitidos
    LOGIN_RATE_WINDOW_SEC: int = 900    # ventana (15 min)

    # ─── IA — claves por entorno, NUNCA hardcode ────────────────────────────
    # Proveedor por defecto cuando un agente no especifica uno: "claude" | "openai"
    DEFAULT_AI_PROVIDER: str = "claude"

    ANTHROPIC_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None   # Google AI Studio — tiene capa GRATIS

    # Modelos por defecto de cada proveedor
    CLAUDE_DEFAULT_MODEL: str = "claude-opus-4-8"
    OPENAI_DEFAULT_MODEL: str = "gpt-4o"
    GEMINI_DEFAULT_MODEL: str = "gemini-2.0-flash"

    # Tipo de cambio USD→CLP para reportar costos (configurable / actualizable)
    USD_TO_CLP: float = 950.0

    @property
    def DATABASE_URL(self) -> str:
        if self.DATABASE_URL_OVERRIDE:
            return self.DATABASE_URL_OVERRIDE
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
