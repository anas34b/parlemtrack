"""Routes des députés : annuaire filtré paginé, fiche avec historique de votes."""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from backend.app.core.config import get_settings
from backend.app.core.db import get_db
from backend.app.core.security import limiter
from backend.app.schemas.depute import DeputeFiche, DeputeOut
from backend.app.schemas.pagination import Page
from backend.app.services.deputes_service import lister_deputes, obtenir_depute

router = APIRouter(prefix="/api/deputes", tags=["Députés"])


@router.get("", response_model=Page[DeputeOut], summary="Annuaire des députés")
@limiter.limit(get_settings().rate_limit)
def liste_deputes(
    request: Request,
    page: int = Query(1, ge=1),
    taille_page: int = Query(20, ge=1, le=100),
    groupe: str | None = Query(None, description="Filtrer par identifiant de groupe"),
    departement: str | None = Query(None),
    actif: bool | None = Query(None, description="true = en exercice, false = remplacé, absent = tous"),
    db: Session = Depends(get_db),
) -> Page[DeputeOut]:
    """Liste paginée des députés, filtrable par groupe, département et statut actif."""
    return lister_deputes(db, page, taille_page, groupe, departement, actif)


@router.get("/{id_an}", response_model=DeputeFiche, summary="Fiche d'un député")
@limiter.limit(get_settings().rate_limit)
def fiche_depute(
    request: Request,
    id_an: str,
    page_votes: int = Query(1, ge=1),
    taille_page_votes: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> DeputeFiche:
    """Identité, groupe, scores et historique de votes paginé d'un député."""
    resultat = obtenir_depute(db, id_an, page_votes, taille_page_votes)
    if resultat is None:
        raise HTTPException(status_code=404, detail="Député introuvable")
    depute, historique = resultat
    return DeputeFiche(depute=depute, historique_votes=historique)
