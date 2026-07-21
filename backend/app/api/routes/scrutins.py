"""Routes des scrutins : liste filtrée paginée, détail avec votes par groupe."""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from backend.app.core.config import get_settings
from backend.app.core.db import get_db
from backend.app.core.security import limiter
from backend.app.schemas.pagination import Page
from backend.app.schemas.scrutin import ScrutinDetail, ScrutinOut
from backend.app.services.scrutins_service import lister_scrutins, obtenir_scrutin

router = APIRouter(prefix="/api/scrutins", tags=["Scrutins"])


@router.get("", response_model=Page[ScrutinOut], summary="Liste des scrutins")
@limiter.limit(get_settings().rate_limit)
def liste_scrutins(
    request: Request,
    page: int = Query(1, ge=1),
    taille_page: int = Query(20, ge=1, le=100),
    groupe: str | None = Query(None, description="Filtrer les scrutins où ce groupe a voté"),
    date_min: date | None = Query(None),
    date_max: date | None = Query(None),
    type: str | None = Query(None, description="Type de vote (ex. scrutin public ordinaire)"),
    q: str | None = Query(None, description="Recherche texte dans le titre"),
    db: Session = Depends(get_db),
) -> Page[ScrutinOut]:
    """Liste paginée des scrutins, filtrable par groupe, période, type et texte du titre."""
    return lister_scrutins(db, page, taille_page, groupe, date_min, date_max, type, q)


@router.get("/{uid}", response_model=ScrutinDetail, summary="Détail d'un scrutin")
@limiter.limit(get_settings().rate_limit)
def detail_scrutin(request: Request, uid: str, db: Session = Depends(get_db)) -> ScrutinDetail:
    """Synthèse des voix, votes par groupe et analyse IA (si disponible) d'un scrutin."""
    resultat = obtenir_scrutin(db, uid)
    if resultat is None:
        raise HTTPException(status_code=404, detail="Scrutin introuvable")
    return resultat
