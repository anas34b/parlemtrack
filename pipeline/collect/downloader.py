"""Téléchargement des archives ZIP de l'Assemblée nationale avec détection de changement.

Une requête HEAD compare l'ETag/Last-Modified distant avec ceux stockés en
base lors de la dernière collecte : si identiques, on ne retélécharge pas.
"""

import io
import logging
import zipfile

import requests
from sqlalchemy.orm import Session

from pipeline.store.collecte import get_source_meta, upsert_source_meta

logger = logging.getLogger("pipeline.collect.downloader")

TIMEOUT_S = 30


def a_change(session: Session, source: str, url: str) -> bool:
    """Compare l'ETag/Last-Modified distant à ceux de la dernière collecte connue."""
    reponse = requests.head(url, timeout=TIMEOUT_S, allow_redirects=True)
    reponse.raise_for_status()
    etag_distant = reponse.headers.get("ETag")
    last_modified_distant = reponse.headers.get("Last-Modified")

    meta = get_source_meta(session, source)
    if meta is None:
        return True
    return meta.etag != etag_distant or meta.last_modified != last_modified_distant


def telecharger_zip(session: Session, source: str, url: str) -> zipfile.ZipFile | None:
    """Télécharge et ouvre l'archive ZIP d'une source, sauf si elle est inchangée.

    Retourne None si la source n'a pas changé depuis la dernière collecte.
    """
    if not a_change(session, source, url):
        logger.info("source %s inchangée depuis la dernière collecte, téléchargement sauté", source)
        return None

    reponse = requests.get(url, timeout=TIMEOUT_S)
    reponse.raise_for_status()
    upsert_source_meta(session, source, reponse.headers.get("ETag"), reponse.headers.get("Last-Modified"))

    logger.info("source %s téléchargée (%d octets)", source, len(reponse.content))
    return zipfile.ZipFile(io.BytesIO(reponse.content))
