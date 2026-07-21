"""Route des dernières actualités presse (cache Redis alimenté par le pipeline)."""

from fastapi import APIRouter, Request

from backend.app.core.config import get_settings
from backend.app.core.security import limiter
from backend.app.schemas.actualite import ActualiteOut
from backend.app.services.actualites_service import lister_actualites

router = APIRouter(prefix="/api/actualites", tags=["Actualités"])


@router.get("", response_model=list[ActualiteOut], summary="Dernières actualités presse")
@limiter.limit(get_settings().rate_limit)
def actualites(request: Request) -> list[ActualiteOut]:
    """Derniers titres des flux RSS presse suivis, collectés par le pipeline."""
    return lister_actualites()
