from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

_url = settings.DATABASE_URL

if _url.startswith("sqlite"):
    # Desarrollo local sin Docker
    engine = create_engine(_url, connect_args={"check_same_thread": False}, pool_pre_ping=True)
else:
    engine = create_engine(
        _url,
        pool_pre_ping=True,     # detecta conexiones muertas antes de usarlas
        pool_recycle=1800,      # recicla conexiones cada 30 min
        pool_size=10,
        max_overflow=20,
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
