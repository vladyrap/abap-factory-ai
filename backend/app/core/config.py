from __future__ import annotations
from pydantic_settings import BaseSettings
from typing import Optional, List


class Settings(BaseSettings):
    PROJECT_NAME: str = "ABAP Factory AI"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"

    SECRET_KEY: str = "change-me-in-production-use-a-long-random-string"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24h

    # PostgreSQL — puertos propios para no chocar con otros proyectos locales
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "abap_factory"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 6602

    CORS_ORIGINS: List[str] = ["http://localhost:6600", "http://localhost:5173"]

    LOG_LEVEL: str = "INFO"
    APP_PUBLIC_URL: str = "http://localhost:6600"

    # ─── IA — claves por entorno, NUNCA hardcode ────────────────────────────
    # Proveedor por defecto cuando un agente no especifica uno: "claude" | "openai"
    DEFAULT_AI_PROVIDER: str = "claude"

    ANTHROPIC_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None

    # Modelos por defecto de cada proveedor
    CLAUDE_DEFAULT_MODEL: str = "claude-opus-4-8"
    OPENAI_DEFAULT_MODEL: str = "gpt-4o"

    # Tipo de cambio USD→CLP para reportar costos (configurable / actualizable)
    USD_TO_CLP: float = 950.0

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
