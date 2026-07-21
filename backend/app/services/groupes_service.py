"""Logique métier des groupes politiques : liste, composition, cohésion des votes."""

from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.app.models import Depute, Groupe, Vote
from backend.app.schemas.groupe import GroupeDetail, GroupeOut


def lister_groupes(db: Session) -> list[GroupeOut]:
    """Liste des groupes politiques (peu nombreux : pas de pagination ni de cache)."""
    groupes = db.query(Groupe).order_by(Groupe.actif.desc(), Groupe.nom).all()
    return [GroupeOut.model_validate(g) for g in groupes]


def _cohesion_moyenne(db: Session, groupe_id: str) -> float | None:
    """Cohésion moyenne : part des votes du groupe alignés sur sa position majoritaire
    par scrutin, moyennée sur tous les scrutins où le groupe s'est exprimé."""
    lignes = (
        db.query(Vote.scrutin_uid, Vote.position, func.count().label("nb"))
        .join(Depute, Vote.depute_id == Depute.id_an)
        .filter(Depute.groupe_id == groupe_id)
        .group_by(Vote.scrutin_uid, Vote.position)
        .all()
    )
    if not lignes:
        return None

    par_scrutin: dict[str, dict[str, int]] = {}
    for scrutin_uid, position, nb in lignes:
        par_scrutin.setdefault(scrutin_uid, {})[position] = nb

    cohesions = [max(positions.values()) / sum(positions.values()) for positions in par_scrutin.values()]
    return round(sum(cohesions) / len(cohesions), 3)


def obtenir_groupe(db: Session, id_an: str) -> GroupeDetail | None:
    """Fiche détaillée d'un groupe : effectif actuel et cohésion moyenne de vote."""
    groupe = db.get(Groupe, id_an)
    if groupe is None:
        return None

    effectif = db.query(Depute).filter(Depute.groupe_id == id_an, Depute.actif.is_(True)).count()
    return GroupeDetail(
        **GroupeOut.model_validate(groupe).model_dump(),
        effectif=effectif,
        cohesion_moyenne=_cohesion_moyenne(db, id_an),
    )
