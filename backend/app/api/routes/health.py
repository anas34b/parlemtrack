"""Route de santé applicative : statut app, base de données, Redis, dernière collecte."""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from backend.app.core.config import get_settings
from backend.app.core.db import get_db
from backend.app.core.security import limiter
from backend.app.schemas.health import HealthOut
from backend.app.services.health_service import obtenir_health

router = APIRouter(prefix="/api/health", tags=["Santé"])


@router.get("", response_model=HealthOut, summary="État de santé de l'application")
@limiter.limit(get_settings().rate_limit)
def health(request: Request, db: Session = Depends(get_db)) -> HealthOut:
    """Vérifie la disponibilité de la base de données et de Redis, et la date de dernière collecte."""
    return obtenir_health(db)
