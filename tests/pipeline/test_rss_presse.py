"""Tests de la récupération RSS presse, réseau mocké."""

from unittest.mock import Mock, patch

from pipeline.collect.rss_presse import parse_entree, recuperer_actualites


def test_parse_entree_normalise_les_champs() -> None:
    entree = {"title": "Titre article", "link": "https://example.org/a", "published": "2026-07-20"}
    resultat = parse_entree(entree, "Le Monde")

    assert resultat["source"] == "Le Monde"
    assert resultat["titre"] == "Titre article"
    assert resultat["lien"] == "https://example.org/a"


def test_parse_entree_champs_absents_valeurs_par_defaut() -> None:
    resultat = parse_entree({}, "Le Figaro")
    assert resultat["titre"] == ""
    assert resultat["lien"] == ""


def _flux_ok(entries: list[dict]) -> Mock:
    flux = Mock()
    flux.bozo = False
    flux.entries = entries
    return flux


def _flux_en_echec() -> Mock:
    flux = Mock()
    flux.bozo = True
    flux.bozo_exception = Exception("flux invalide")
    flux.entries = []
    return flux


def test_recuperer_actualites_agrege_les_flux() -> None:
    with patch(
        "pipeline.collect.rss_presse.feedparser.parse",
        return_value=_flux_ok([{"title": "A", "link": "https://x", "published": "2026-07-20"}]),
    ):
        resultat = recuperer_actualites()

    assert len(resultat) == 3 * 1  # 3 flux configurés, 1 entrée chacun
    assert all(a["titre"] == "A" for a in resultat)


def test_recuperer_actualites_flux_en_echec_ignore_sans_lever() -> None:
    with patch("pipeline.collect.rss_presse.feedparser.parse", return_value=_flux_en_echec()):
        resultat = recuperer_actualites()

    assert resultat == []
