"""Moteur SQLAlchemy et dépendance FastAPI de session de base de données."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.app.core.config import get_settings

engine = create_engine(get_settings().database_url)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db() -> Generator[Session, None, None]:
    """Fournit une session de base de données par requête, fermée en fin d'appel."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
