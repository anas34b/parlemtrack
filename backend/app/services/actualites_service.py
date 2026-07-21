"""Lecture des actualités presse mises en cache par le pipeline (Phase 1)."""

from backend.app.core.cache import get_redis
from backend.app.schemas.actualite import ActualiteOut
from pipeline.store.actualites_cache import lire_actualites


def lister_actualites() -> list[ActualiteOut]:
    """Retourne les derniers titres presse collectés, ou une liste vide si rien en cache."""
    return [ActualiteOut(**a) for a in lire_actualites(get_redis())]
