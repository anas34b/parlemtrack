"""Point d'entrée du pipeline : collecte, parsing, stockage, résumé de run.

Lancement : `python -m pipeline.run`
"""

import json
import time

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from backend.app.core.config import Settings, get_settings
from backend.app.core.logging import get_logger, setup_logging
from backend.app.models import Depute
from pipeline.collect.datan import mettre_a_jour_scores, recuperer_scores_datan
from pipeline.collect.downloader import telecharger_zip
from pipeline.collect.rss_presse import recuperer_actualites
from pipeline.parse.deputes import a_mandat_assemblee, parse_depute
from pipeline.parse.organes import parse_groupe
from pipeline.parse.scrutins import parse_scrutin
from pipeline.store.actualites_cache import enregistrer_actualites
from pipeline.store.collecte import log_collecte
from pipeline.store.upsert import (
    desactiver_deputes_absents,
    upsert_depute,
    upsert_groupe,
    upsert_scrutin,
)

logger = get_logger("pipeline.run")

URL_SCRUTINS = "https://data.assemblee-nationale.fr/static/openData/repository/17/loi/scrutins/Scrutins.json.zip"
URL_DEPUTES = (
    "https://data.assemblee-nationale.fr/static/openData/repository/17/amo/"
    "deputes_actifs_mandats_actifs_organes/AMO10_deputes_actifs_mandats_actifs_organes.json.zip"
)
URL_DEPUTES_HISTORIQUE = (
    "https://data.assemblee-nationale.fr/static/openData/repository/17/amo/"
    "tous_acteurs_mandats_organes_xi_legislature/"
    "AMO30_tous_acteurs_tous_mandats_tous_organes_historique.json.zip"
)


def _upserter_groupes(session: Session, archive, ids_deja_traites: set[str]) -> None:
    """Upserte les groupes politiques (GP, législature 17) trouvés dans `json/organe/*.json`.

    `ids_deja_traites` évite de compter deux fois un même groupe présent
    dans les deux archives (actifs et historique se recoupent).
    """
    for nom in archive.namelist():
        if not nom.startswith("json/organe/"):
            continue
        groupe = parse_groupe(json.loads(archive.read(nom)))
        if groupe is not None:
            upsert_groupe(session, groupe)
            ids_deja_traites.add(groupe["id_an"])


def _collecter_deputes_et_groupes(session: Session) -> tuple[int, int, int]:
    """Upserte les groupes et les députés : jeu "actifs" (AMO10) puis remplacés (AMO30).

    Un député remplacé en cours de législature (décès, entrée au
    gouvernement, invalidation d'élection) n'apparaît plus dans AMO10 mais
    reste référencé par les votes des scrutins passés (voir BUG-003) : on le
    retrouve dans l'historique complet AMO30 et on l'insère avec `actif=False`.
    """
    ids_groupes = set()
    archive_actifs = telecharger_zip(session, "deputes", URL_DEPUTES)
    nb_deputes_actifs = 0
    if archive_actifs is not None:
        _upserter_groupes(session, archive_actifs, ids_groupes)
        ids_amo10_ce_run = set()
        for nom in archive_actifs.namelist():
            if not nom.startswith("json/acteur/"):
                continue
            depute = parse_depute(json.loads(archive_actifs.read(nom)), actif=True)
            upsert_depute(session, depute)
            ids_amo10_ce_run.add(depute["id_an"])
            nb_deputes_actifs += 1

        if ids_amo10_ce_run:
            for depute_desactive in desactiver_deputes_absents(session, ids_amo10_ce_run):
                logger.info(
                    "député remplacé, passage à actif=False : %s %s (%s)",
                    depute_desactive.prenom,
                    depute_desactive.nom,
                    depute_desactive.id_an,
                )

    ids_actifs = {
        row[0] for row in session.execute(select(Depute.id_an).where(Depute.actif.is_(True)))
    }

    archive_historique = telecharger_zip(session, "deputes_historique", URL_DEPUTES_HISTORIQUE)
    nb_deputes_inactifs = 0
    if archive_historique is not None:
        _upserter_groupes(session, archive_historique, ids_groupes)
        for nom in archive_historique.namelist():
            if not nom.startswith("json/acteur/"):
                continue
            raw = json.loads(archive_historique.read(nom))
            depute = parse_depute(raw, actif=False)
            if depute["id_an"] in ids_actifs or not a_mandat_assemblee(raw):
                continue
            upsert_depute(session, depute)
            nb_deputes_inactifs += 1

    return len(ids_groupes), nb_deputes_actifs, nb_deputes_inactifs


def _collecter_scrutins(session: Session) -> tuple[int, int, int]:
    """Télécharge et upserte les scrutins (un fichier JSON par scrutin dans l'archive)."""
    archive = telecharger_zip(session, "scrutins", URL_SCRUTINS)
    if archive is None:
        return 0, 0, 0

    nb_traites, nb_nouveaux, nb_erreurs = 0, 0, 0
    for nom in archive.namelist():
        if not nom.endswith(".json"):
            continue
        try:
            raw = json.loads(archive.read(nom))
            est_nouveau = upsert_scrutin(session, parse_scrutin(raw))
            nb_traites += 1
            nb_nouveaux += int(est_nouveau)
        except (KeyError, ValueError) as exc:
            logger.error("échec du parsing de %s : %s", nom, exc)
            nb_erreurs += 1

    return nb_traites, nb_nouveaux, nb_erreurs


def _taches_non_critiques(session: Session, settings: Settings) -> None:
    """Scores Datan, actualités RSS, invalidation du cache API.

    Chaque tâche est isolée dans son propre try/except : un échec ici ne
    doit jamais faire perdre la collecte principale (scrutins/députés).
    """
    try:
        scores = recuperer_scores_datan()
        nb_scores = mettre_a_jour_scores(session, scores)
        session.commit()
        logger.info("%d scores Datan mis à jour", nb_scores)
    except Exception as exc:
        session.rollback()
        logger.warning("mise à jour des scores Datan échouée : %s", exc)

    try:
        import redis

        client = redis.from_url(settings.redis_url, decode_responses=True)
        enregistrer_actualites(client, recuperer_actualites())
    except Exception as exc:
        logger.warning("collecte des actualités RSS échouée : %s", exc)

    try:
        from backend.app.core.cache import invalider_prefixe

        for prefixe in ("cache:scrutins", "cache:deputes"):
            invalider_prefixe(prefixe)
        logger.info("cache API invalidé")
    except Exception as exc:
        logger.warning("invalidation du cache API échouée : %s", exc)


def executer_pipeline() -> None:
    """Orchestre un run complet : collecte, parsing, stockage, résumé."""
    setup_logging()
    debut = time.monotonic()
    settings = get_settings()
    engine = create_engine(settings.database_url)

    nb_erreurs = 0
    with Session(engine) as session:
        try:
            nb_groupes, nb_deputes_actifs, nb_deputes_inactifs = _collecter_deputes_et_groupes(
                session
            )
            logger.info(
                "%d groupes, %d députés actifs et %d députés remplacés traités",
                nb_groupes,
                nb_deputes_actifs,
                nb_deputes_inactifs,
            )

            nb_scrutins, nb_nouveaux, nb_erreurs = _collecter_scrutins(session)

            session.commit()
        except Exception:
            session.rollback()
            raise

        _taches_non_critiques(session, settings)

        duree_s = time.monotonic() - debut
        log_collecte(
            session,
            nb_scrutins_traites=nb_scrutins,
            nb_nouveaux=nb_nouveaux,
            nb_analyses_generees=0,
            nb_erreurs=nb_erreurs,
            duree_s=duree_s,
            statut="succes" if nb_erreurs == 0 else "partiel",
        )
        session.commit()

    logger.info(
        "run terminé : %d scrutins traités, %d nouveaux, %d erreurs, %.1fs",
        nb_scrutins,
        nb_nouveaux,
        nb_erreurs,
        duree_s,
    )


if __name__ == "__main__":
    executer_pipeline()
