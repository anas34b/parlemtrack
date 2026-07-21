"""Tests du parser d'organes : filtrage des groupes politiques (GP) de la législature 17."""

import json
from pathlib import Path

from pipeline.parse.organes import parse_groupe

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


def _load(nom: str) -> dict:
    return json.loads((FIXTURES / nom).read_text(encoding="utf-8"))


def test_groupe_politique_actif_est_parse() -> None:
    resultat = parse_groupe(_load("organe_groupe_politique.json"))

    assert resultat is not None
    assert resultat["id_an"] == "PO845401"
    assert resultat["nom"] == "Ensemble pour la République"
    assert resultat["nom_court"] == "EPR"
    assert resultat["couleur"] == "#0f62a4"
    assert resultat["actif"] is True


def test_groupe_politique_dissous_est_marque_inactif() -> None:
    resultat = parse_groupe(_load("organe_groupe_dissous.json"))

    assert resultat is not None
    assert resultat["actif"] is False


def test_organe_non_gp_est_ignore() -> None:
    """Une circonscription n'est pas un groupe politique : parse_groupe renvoie None."""
    resultat = parse_groupe(_load("organe_circonscription.json"))
    assert resultat is None


def test_organe_gp_autre_legislature_est_ignore() -> None:
    """L'historique AMO30 couvre toutes les législatures : on ne garde que la 17e."""
    resultat = parse_groupe(_load("organe_groupe_autre_legislature.json"), legislature="17")
    assert resultat is None
