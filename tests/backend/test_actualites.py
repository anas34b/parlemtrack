"""Tests de la route /api/actualites."""

from backend.app.core.cache import get_redis
from pipeline.store.actualites_cache import enregistrer_actualites


def test_actualites_vide_si_rien_en_cache(client) -> None:
    reponse = client.get("/api/actualites")
    assert reponse.status_code == 200
    assert reponse.json() == []


def test_actualites_lit_le_cache_alimente_par_le_pipeline(client) -> None:
    actualite = {"source": "Le Monde", "titre": "Titre", "lien": "https://x", "date_publication": "2026-07-20"}
    enregistrer_actualites(get_redis(), [actualite])

    reponse = client.get("/api/actualites")

    assert reponse.status_code == 200
    assert reponse.json() == [actualite]
