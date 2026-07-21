"""Tests du cache Redis des actualités presse, contre une vraie instance Redis locale."""

import pytest
import redis

from backend.app.core.config import get_settings
from pipeline.store.actualites_cache import CLE_REDIS, enregistrer_actualites, lire_actualites


@pytest.fixture
def redis_client():
    """Base Redis dédiée aux tests (index 1), distincte de celle du pipeline (index 0)."""
    url_test = get_settings().redis_url.rsplit("/", 1)[0] + "/1"
    client = redis.from_url(url_test, decode_responses=True)
    client.delete(CLE_REDIS)
    yield client
    client.delete(CLE_REDIS)


def test_lire_actualites_vide_si_rien_en_cache(redis_client) -> None:
    assert lire_actualites(redis_client) == []


def test_enregistrer_puis_lire_actualites(redis_client) -> None:
    actualites = [{"source": "Le Monde", "titre": "Titre", "lien": "https://x", "date_publication": "2026-07-20"}]
    enregistrer_actualites(redis_client, actualites)

    assert lire_actualites(redis_client) == actualites
