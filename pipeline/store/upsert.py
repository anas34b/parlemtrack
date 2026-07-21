"""Insertions/mises à jour idempotentes en base : upsert pour les entités, jamais de suppression."""

import logging

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from backend.app.models import AnalyseIA, Depute, Groupe, Scrutin, Vote

logger = logging.getLogger("pipeline.store.upsert")


def upsert_groupe(session: Session, data: dict) -> None:
    """Insère un groupe, ou met à jour son nom/couleur/statut actif s'il existe déjà."""
    stmt = insert(Groupe).values(**data)
    stmt = stmt.on_conflict_do_update(
        index_elements=["id_an"],
        set_={
            "nom": stmt.excluded.nom,
            "nom_court": stmt.excluded.nom_court,
            "actif": stmt.excluded.actif,
            "couleur": stmt.excluded.couleur,
        },
    )
    session.execute(stmt)


def upsert_depute(session: Session, data: dict) -> None:
    """Insère un député, ou met à jour son groupe/statut actif s'il existe déjà."""
    stmt = insert(Depute).values(**data)
    stmt = stmt.on_conflict_do_update(
        index_elements=["id_an"],
        set_={
            "nom": stmt.excluded.nom,
            "prenom": stmt.excluded.prenom,
            "actif": stmt.excluded.actif,
            "groupe_id": stmt.excluded.groupe_id,
        },
    )
    session.execute(stmt)


def desactiver_deputes_absents(session: Session, ids_actifs_courants: set[str]) -> list[Depute]:
    """Repasse `actif=False` les députés marqués actifs mais absents du jeu AMO10 courant.

    Ne supprime jamais rien : c'est la bascule automatique qui garde la
    colonne `actif` fiable d'un run à l'autre (voir BUG-003). Retourne les
    députés basculés, pour que l'appelant puisse les journaliser.

    ATTENTION : `ids_actifs_courants` doit représenter un jeu AMO10
    réellement téléchargé ce run. Un appel avec un ensemble vide ou
    incomplet désactiverait à tort tous les députés absents de ce jeu.
    """
    a_desactiver = list(
        session.execute(
            select(Depute).where(Depute.actif.is_(True)).where(Depute.id_an.notin_(ids_actifs_courants))
        ).scalars()
    )
    if not a_desactiver:
        return []
    ids = [d.id_an for d in a_desactiver]
    session.execute(update(Depute).where(Depute.id_an.in_(ids)).values(actif=False))
    return a_desactiver


def upsert_scrutin(session: Session, data: dict) -> bool:
    """Insère un scrutin (et ses votes), ou met à jour la synthèse s'il existe déjà.

    Retourne True si le scrutin était nouveau (pour le compteur de collecte).
    """
    votes = data.pop("votes", [])
    nouveau = session.execute(select(Scrutin.uid).where(Scrutin.uid == data["uid"])).first() is None

    stmt = insert(Scrutin).values(**data)
    stmt = stmt.on_conflict_do_update(
        index_elements=["uid"],
        set_={
            "nb_pour": stmt.excluded.nb_pour,
            "nb_contre": stmt.excluded.nb_contre,
            "nb_abstention": stmt.excluded.nb_abstention,
            "nb_non_votants": stmt.excluded.nb_non_votants,
        },
    )
    session.execute(stmt)
    insert_votes(session, data["uid"], votes)
    return nouveau


def inserer_analyse_ia(session: Session, scrutin_uid: str, analyse: dict) -> None:
    """Insère l'analyse IA d'un scrutin — une seule fois, jamais mise à jour ensuite.

    `ON CONFLICT DO NOTHING` : si une analyse existe déjà pour ce scrutin
    (ré-exécution accidentelle), elle est conservée telle quelle.
    """
    stmt = insert(AnalyseIA).values(scrutin_uid=scrutin_uid, **analyse)
    stmt = stmt.on_conflict_do_nothing(index_elements=["scrutin_uid"])
    session.execute(stmt) 


def insert_votes(session: Session, scrutin_uid: str, votes: list[dict]) -> None:
    """Insère les votes d'un scrutin, ignore les doublons (scrutin_uid, depute_id).

    Un vote peut référencer un député absent du jeu "actifs" (remplacé en
    cours de législature) : il est ignoré avec un WARNING plutôt que de
    faire échouer tout le scrutin sur une contrainte de clé étrangère.
    """
    if not votes:
        return
    depute_ids = {vote["depute_id"] for vote in votes}
    connus = {
        row[0]
        for row in session.execute(select(Depute.id_an).where(Depute.id_an.in_(depute_ids)))
    }
    inconnus = depute_ids - connus
    if inconnus:
        logger.warning(
            "scrutin %s : %d vote(s) ignoré(s), député(s) inconnu(s) %s",
            scrutin_uid,
            len(inconnus),
            sorted(inconnus),
        )

    votes_valides = [v for v in votes if v["depute_id"] in connus]
    if not votes_valides:
        return
    for vote in votes_valides:
        vote["scrutin_uid"] = scrutin_uid
    stmt = insert(Vote).values(votes_valides)
    stmt = stmt.on_conflict_do_nothing(constraint="uq_scrutin_depute")
    session.execute(stmt)
