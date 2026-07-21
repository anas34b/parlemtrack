"""Routes des groupes politiques : liste, fiche détaillée (composition, cohésion)."""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from backend.app.core.config import get_settings
from backend.app.core.db import get_db
from backend.app.core.security import limiter
from backend.app.schemas.groupe import GroupeDetail, GroupeOut
from backend.app.services.groupes_service import lister_groupes, obtenir_groupe

router = APIRouter(prefix="/api/groupes", tags=["Groupes"])


@router.get("", response_model=list[GroupeOut], summary="Liste des groupes politiques")
@limiter.limit(get_settings().rate_limit)
def liste_groupes(request: Request, db: Session = Depends(get_db)) -> list[GroupeOut]:
    """Tous les groupes politiques de la législature, actifs et dissous."""
    return lister_groupes(db)


@router.get("/{id_an}", response_model=GroupeDetail, summary="Détail d'un groupe politique")
@limiter.limit(get_settings().rate_limit)
def detail_groupe(request: Request, id_an: str, db: Session = Depends(get_db)) -> GroupeDetail:
    """Effectif actuel et cohésion moyenne de vote d'un groupe politique."""
    resultat = obtenir_groupe(db, id_an)
    if resultat is None:
        raise HTTPException(status_code=404, detail="Groupe introuvable")
    return resultat
