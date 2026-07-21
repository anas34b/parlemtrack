"""Route de recherche unifiée député / groupe / scrutin."""

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from backend.app.core.config import get_settings
from backend.app.core.db import get_db
from backend.app.core.security import limiter
from backend.app.schemas.recherche import RechercheResultat
from backend.app.services.recherche_service import rechercher

router = APIRouter(prefix="/api/recherche", tags=["Recherche"])


@router.get("", response_model=RechercheResultat, summary="Recherche unifiée")
@limiter.limit(get_settings().rate_limit)
def recherche(
    request: Request,
    q: str = Query(..., min_length=1, description="Texte recherché"),
    db: Session = Depends(get_db),
) -> RechercheResultat:
    """Recherche `q` parmi les députés, groupes et scrutins, résultats groupés par type."""
    return rechercher(db, q)
