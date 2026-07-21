"""Logique métier des scrutins : listing filtré, détail avec votes par groupe."""

from datetime import date

from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.app.core.cache import get_cache, set_cache
from backend.app.models import AnalyseIA, Depute, Groupe, Scrutin, Vote
from backend.app.schemas.pagination import Page
from backend.app.schemas.scrutin import ScrutinDetail, ScrutinOut, VoteParGroupeOut

PREFIXE_CACHE = "cache:scrutins"


def lister_scrutins(
    db: Session,
    page: int,
    taille_page: int,
    groupe_id: str | None = None,
    date_min: date | None = None,
    date_max: date | None = None,
    type_vote: str | None = None,
    q: str | None = None,
) -> Page[ScrutinOut]:
    """Liste paginée et filtrée des scrutins, mise en cache Redis."""
    cle = f"{PREFIXE_CACHE}:liste:{page}:{taille_page}:{groupe_id}:{date_min}:{date_max}:{type_vote}:{q}"
    en_cache = get_cache(cle)
    if en_cache is not None:
        return Page[ScrutinOut](**en_cache)

    requete = db.query(Scrutin)
    if groupe_id is not None:
        requete = requete.filter(
            Scrutin.uid.in_(
                db.query(Vote.scrutin_uid).join(Depute, Vote.depute_id == Depute.id_an).filter(
                    Depute.groupe_id == groupe_id
                )
            )
        )
    if date_min is not None:
        requete = requete.filter(Scrutin.date_scrutin >= date_min)
    if date_max is not None:
        requete = requete.filter(Scrutin.date_scrutin <= date_max)
    if type_vote is not None:
        requete = requete.filter(Scrutin.type_vote == type_vote)
    if q is not None:
        requete = requete.filter(Scrutin.titre.ilike(f"%{q}%"))

    total = requete.count()
    items = (
        requete.order_by(Scrutin.date_scrutin.desc(), Scrutin.numero.desc())
        .offset((page - 1) * taille_page)
        .limit(taille_page)
        .all()
    )
    resultat = Page[ScrutinOut](
        items=[ScrutinOut.model_validate(s) for s in items], total=total, page=page, taille_page=taille_page
    )
    set_cache(cle, resultat.model_dump(mode="json"))
    return resultat


def obtenir_scrutin(db: Session, uid: str) -> ScrutinDetail | None:
    """Détail d'un scrutin : synthèse, votes agrégés par groupe, analyse IA si disponible."""
    cle = f"{PREFIXE_CACHE}:detail:{uid}"
    en_cache = get_cache(cle)
    if en_cache is not None:
        return ScrutinDetail(**en_cache)

    scrutin = db.get(Scrutin, uid)
    if scrutin is None:
        return None

    lignes = (
        db.query(
            Groupe.id_an,
            Groupe.nom,
            Vote.position,
            func.count().label("nb"),
        )
        .join(Depute, Vote.depute_id == Depute.id_an)
        .join(Groupe, Depute.groupe_id == Groupe.id_an)
        .filter(Vote.scrutin_uid == uid)
        .group_by(Groupe.id_an, Groupe.nom, Vote.position)
        .all()
    )
    par_groupe: dict[str, VoteParGroupeOut] = {}
    for groupe_id, groupe_nom, position, nb in lignes:
        entree = par_groupe.setdefault(
            groupe_id,
            VoteParGroupeOut(
                groupe_id=groupe_id, groupe_nom=groupe_nom, pour=0, contre=0, abstention=0, non_votant=0
            ),
        )
        if position == "pour":
            entree.pour = nb
        elif position == "contre":
            entree.contre = nb
        elif position == "abstention":
            entree.abstention = nb
        elif position in ("nonVotant", "nonVotantVolontaire"):
            entree.non_votant += nb

    analyse = db.get(AnalyseIA, uid)
    resultat = ScrutinDetail(
        **ScrutinOut.model_validate(scrutin).model_dump(),
        dossier_ref=scrutin.dossier_ref,
        votes_par_groupe=list(par_groupe.values()),
        analyse_ia=analyse,
    )
    set_cache(cle, resultat.model_dump(mode="json"))
    return resultat
