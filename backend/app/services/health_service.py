"""Vérification de l'état de l'application et de ses dépendances directes."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.core.cache import get_redis
from backend.app.models import CollecteLog
from backend.app.schemas.health import HealthOut


def obtenir_health(db: Session) -> HealthOut:
    """Interroge la base et Redis, sans jamais lever si l'un des deux est indisponible."""
    try:
        db.execute(select(1))
        db_ok = True
    except Exception:
        db_ok = False

    try:
        get_redis().ping()
        redis_ok = True
    except Exception:
        redis_ok = False

    derniere_collecte = None
    if db_ok:
        derniere_collecte = db.execute(select(func.max(CollecteLog.date_run))).scalar()

    return HealthOut(
        statut="ok" if db_ok and redis_ok else "degrade",
        base_de_donnees=db_ok,
        redis=redis_ok,
        derniere_collecte=derniere_collecte,
    )
