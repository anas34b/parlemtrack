"""Logique métier des députés : annuaire filtré, fiche avec historique de votes."""

from sqlalchemy.orm import Session

from backend.app.core.cache import get_cache, set_cache
from backend.app.models import Depute, Scrutin, Vote
from backend.app.schemas.depute import DeputeDetail, DeputeOut, VoteHistoriqueOut
from backend.app.schemas.pagination import Page

PREFIXE_CACHE = "cache:deputes"


def lister_deputes(
    db: Session,
    page: int,
    taille_page: int,
    groupe_id: str | None = None,
    departement: str | None = None,
    actif: bool | None = None,
) -> Page[DeputeOut]:
    """Liste paginée et filtrée des députés, mise en cache Redis.

    `actif=None` (défaut) renvoie tous les députés, y compris les remplacés
    en cours de législature (voir BUG-003) : c'est au client (frontend) de
    passer `actif=true` pour n'afficher que les députés en exercice.
    """
    cle = f"{PREFIXE_CACHE}:liste:{page}:{taille_page}:{groupe_id}:{departement}:{actif}"
    en_cache = get_cache(cle)
    if en_cache is not None:
        return Page[DeputeOut](**en_cache)

    requete = db.query(Depute)
    if groupe_id is not None:
        requete = requete.filter(Depute.groupe_id == groupe_id)
    if departement is not None:
        requete = requete.filter(Depute.departement == departement)
    if actif is not None:
        requete = requete.filter(Depute.actif.is_(actif))

    total = requete.count()
    items = (
        requete.order_by(Depute.nom, Depute.prenom)
        .offset((page - 1) * taille_page)
        .limit(taille_page)
        .all()
    )
    resultat = Page[DeputeOut](
        items=[DeputeOut.model_validate(d) for d in items], total=total, page=page, taille_page=taille_page
    )
    set_cache(cle, resultat.model_dump(mode="json"))
    return resultat


def obtenir_depute(
    db: Session, id_an: str, page_votes: int, taille_page_votes: int
) -> tuple[DeputeDetail, Page[VoteHistoriqueOut]] | None:
    """Fiche complète d'un député et son historique de votes paginé (non caché : requête ciblée légère)."""
    depute = db.get(Depute, id_an)
    if depute is None:
        return None

    requete_votes = (
        db.query(Vote, Scrutin.titre, Scrutin.date_scrutin)
        .join(Scrutin, Vote.scrutin_uid == Scrutin.uid)
        .filter(Vote.depute_id == id_an)
    )
    total_votes = requete_votes.count()
    lignes = (
        requete_votes.order_by(Scrutin.date_scrutin.desc())
        .offset((page_votes - 1) * taille_page_votes)
        .limit(taille_page_votes)
        .all()
    )
    historique = Page[VoteHistoriqueOut](
        items=[
            VoteHistoriqueOut(
                scrutin_uid=vote.scrutin_uid,
                scrutin_titre=titre,
                scrutin_date=date_scrutin,
                position=vote.position,
                par_delegation=vote.par_delegation,
            )
            for vote, titre, date_scrutin in lignes
        ],
        total=total_votes,
        page=page_votes,
        taille_page=taille_page_votes,
    )
    return DeputeDetail.model_validate(depute), historique
