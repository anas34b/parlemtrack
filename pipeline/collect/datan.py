"""Mise à jour hebdomadaire des scores Datan (participation, loyauté, majorité).

Job séparé : ne crée jamais de nouveau député, met seulement à jour les
scores des députés déjà présents en base (upsert des scrutins/deputes).
"""

import csv
import io
import logging

import requests
from sqlalchemy import update
from sqlalchemy.orm import Session

from backend.app.models import Depute

logger = logging.getLogger("pipeline.collect.datan")

URL_DATASET_API = "https://www.data.gouv.fr/api/1/datasets/5fc8b732d30fbf1ed6648aab/"
TIMEOUT_S = 30


def _resoudre_url_csv() -> str:
    """Résout l'URL du CSV Datan via l'API data.gouv.fr.

    L'URL directe du fichier est horodatée et change à chaque republication
    hebdomadaire du dataset : on la code en dur casserait le job à la
    prochaine mise à jour (voir BUG-005). On interroge donc l'API du
    dataset, stable dans le temps, pour obtenir l'URL courante.
    """
    reponse = requests.get(URL_DATASET_API, timeout=TIMEOUT_S)
    reponse.raise_for_status()
    ressources = reponse.json()["resources"]
    return next(r["url"] for r in ressources if r["format"] == "csv")


def _to_float(valeur: str) -> float | None:
    """Convertit une valeur CSV en float, défensivement (champ vide possible)."""
    try:
        return float(valeur)
    except (TypeError, ValueError):
        return None


def parse_ligne_datan(ligne: dict) -> dict:
    """Normalise une ligne du CSV Datan en dict de scores."""
    return {
        "id_an": ligne["id"],
        "score_participation": _to_float(ligne.get("scoreParticipation")),
        "score_loyaute": _to_float(ligne.get("scoreLoyaute")),
        "score_majorite": _to_float(ligne.get("scoreMajorite")),
    }


def recuperer_scores_datan() -> list[dict]:
    """Résout l'URL courante puis télécharge et parse le CSV Datan des scores de députés."""
    url_csv = _resoudre_url_csv()
    reponse = requests.get(url_csv, timeout=TIMEOUT_S)
    reponse.raise_for_status()
    lecteur = csv.DictReader(io.StringIO(reponse.text))
    return [parse_ligne_datan(ligne) for ligne in lecteur]


def mettre_a_jour_scores(session: Session, scores: list[dict]) -> int:
    """Met à jour les scores des députés déjà en base. Retourne le nombre mis à jour."""
    nb_mis_a_jour = 0
    for score in scores:
        resultat = session.execute(
            update(Depute)
            .where(Depute.id_an == score["id_an"])
            .values(
                score_participation=score["score_participation"],
                score_loyaute=score["score_loyaute"],
                score_majorite=score["score_majorite"],
            )
        )
        nb_mis_a_jour += resultat.rowcount
    return nb_mis_a_jour
