"""Sélection des scrutins sans analyse IA et génération par lots, avec suivi coût/tokens.

Tarifs Mistral Large (USD / million de tokens, mistral.ai/pricing) : entrée
2 $, sortie 6 $. On ne dispose que du total de tokens retourné par l'API
(pas du détail entrée/sortie) : le coût est donc estimé avec le tarif le
plus défavorable (sortie) comme majorant prudent.
"""

import logging
import time

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models import AnalyseIA, Depute, Groupe, Scrutin, Vote
from pipeline.ia.mistral_client import generer_analyse
from pipeline.store.upsert import inserer_analyse_ia

logger = logging.getLogger("pipeline.ia.generer_analyses")

PRIX_USD_PAR_MILLION_TOKENS = 6.0
PAUSE_ENTRE_APPELS_S = 1.5


def scrutins_sans_analyse(
    session: Session,
    limite: int | None = None,
    uids: list[str] | None = None,
    type_vote: str | None = None,
) -> list[str]:
    """Liste les uid de scrutins sans analyse IA, les plus récents d'abord.

    `uids` restreint aux scrutins donnés (utile pour une génération ciblée) ;
    `type_vote` filtre par type (ex. "scrutin public solennel") ; `limite`
    plafonne le nombre de résultats (utile pour un lot/une tranche).
    """
    requete = (
        select(Scrutin.uid)
        .outerjoin(AnalyseIA, AnalyseIA.scrutin_uid == Scrutin.uid)
        .where(AnalyseIA.scrutin_uid.is_(None))
        .order_by(Scrutin.date_scrutin.desc())
    )
    if type_vote is not None:
        requete = requete.where(Scrutin.type_vote == type_vote)
    if uids is not None:
        requete = requete.where(Scrutin.uid.in_(uids))
    if limite is not None:
        requete = requete.limit(limite)
    return [row[0] for row in session.execute(requete)]


def _construire_contexte_scrutin(session: Session, uid: str) -> dict:
    """Reconstitue le dict attendu par le prompt builder pour un scrutin donné."""
    scrutin = session.get(Scrutin, uid)
    lignes = (
        session.query(Groupe.nom, Vote.position, Vote.depute_id)
        .join(Depute, Vote.depute_id == Depute.id_an)
        .join(Groupe, Depute.groupe_id == Groupe.id_an)
        .filter(Vote.scrutin_uid == uid)
        .all()
    )
    comptes: dict[str, dict[str, int]] = {}
    for groupe_nom, position, _ in lignes:
        c = comptes.setdefault(groupe_nom, {"pour": 0, "contre": 0, "abstention": 0, "non_votant": 0})
        cle = "non_votant" if position in ("nonVotant", "nonVotantVolontaire") else position
        c[cle] += 1

    return {
        "uid": scrutin.uid,
        "titre": scrutin.titre,
        "date_scrutin": str(scrutin.date_scrutin),
        "type_vote": scrutin.type_vote,
        "sort": scrutin.sort,
        "nb_pour": scrutin.nb_pour,
        "nb_contre": scrutin.nb_contre,
        "nb_abstention": scrutin.nb_abstention,
        "nb_non_votants": scrutin.nb_non_votants,
        "votes_par_groupe": [{"groupe_nom": nom, **c} for nom, c in comptes.items()],
    }


def generer_lot(session: Session, uids: list[str]) -> dict:
    """Génère et stocke l'analyse IA de chaque scrutin de `uids`, dans l'ordre donné.

    Log une ligne de progression par scrutin et un résumé final (nb générées,
    nb erreurs, tokens totaux, coût estimé). Une erreur sur un scrutin est
    loggée et n'interrompt pas le lot.
    """
    nb_generees, nb_erreurs, tokens_totaux = 0, 0, 0
    total = len(uids)
    for index, uid in enumerate(uids, start=1):
        try:
            contexte = _construire_contexte_scrutin(session, uid)
            analyse = generer_analyse(contexte)
            inserer_analyse_ia(session, uid, analyse)
            session.commit()
            nb_generees += 1
            tokens_totaux += analyse["tokens_utilises"]
            logger.info(
                "[%d/%d] analyse générée pour %s (%d tokens)", index, total, uid, analyse["tokens_utilises"]
            )
        except Exception as exc:
            session.rollback()
            nb_erreurs += 1
            logger.error("[%d/%d] échec de l'analyse pour %s : %s", index, total, uid, exc)

        if index < total:
            time.sleep(PAUSE_ENTRE_APPELS_S)

    cout_estime = tokens_totaux / 1_000_000 * PRIX_USD_PAR_MILLION_TOKENS
    logger.info(
        "lot terminé : %d générées, %d erreurs, %d tokens, coût estimé $%.4f",
        nb_generees,
        nb_erreurs,
        tokens_totaux,
        cout_estime,
    )
    return {
        "nb_generees": nb_generees,
        "nb_erreurs": nb_erreurs,
        "tokens_totaux": tokens_totaux,
        "cout_estime": cout_estime,
    }
