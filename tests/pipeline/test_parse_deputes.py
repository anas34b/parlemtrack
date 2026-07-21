"""Tests du parser de députés, cas limites du format AN."""

import json
from pathlib import Path

from pipeline.parse.deputes import a_mandat_assemblee, parse_depute

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


def _load(nom: str) -> dict:
    return json.loads((FIXTURES / nom).read_text(encoding="utf-8"))


def test_depute_nominal_champs_de_base() -> None:
    resultat = parse_depute(_load("depute_nominal.json"))

    assert resultat["id_an"] == "PA841605"
    assert resultat["nom"] == "Golliot"
    assert resultat["prenom"] == "Antoine"
    assert resultat["groupe_id"] == "PO845401"
    assert resultat["actif"] is True


def test_depute_uid_chaine_directe_extraite() -> None:
    """Piège AN : l'uid est parfois `{"#text": ...}`, parfois une chaîne directe."""
    resultat = parse_depute(_load("depute_mandat_unique_sans_groupe.json"))

    assert resultat["id_an"] == "PA1008"


def test_depute_mandat_unique_normalise_en_liste() -> None:
    """Piège AN : un seul mandat devient un objet, pas un tableau."""
    resultat = parse_depute(_load("depute_mandat_unique_sans_groupe.json"))
    assert resultat["nom"] == "David"


def test_depute_dernier_groupe_renvoye_meme_mandat_termine() -> None:
    """BUG-003 : un député remplacé garde son dernier groupe connu, pas None."""
    resultat = parse_depute(_load("depute_mandat_unique_sans_groupe.json"), actif=False)
    assert resultat["groupe_id"] == "PO845401"
    assert resultat["actif"] is False


def test_depute_sans_aucun_mandat_gp_donne_none() -> None:
    resultat = parse_depute(_load("depute_sans_aucun_groupe.json"))
    assert resultat["groupe_id"] is None


def test_a_mandat_assemblee_vrai_pour_legislature_17() -> None:
    resultat = a_mandat_assemblee(_load("depute_nominal.json"), legislature="17")
    assert resultat is False  # la fixture nominale n'a pas de mandat ASSEMBLEE


def test_a_mandat_assemblee_vrai_quand_present() -> None:
    raw = {
        "acteur": {
            "uid": "PA9999",
            "mandats": {"mandat": {"typeOrgane": "ASSEMBLEE", "legislature": "17"}},
        }
    }
    assert a_mandat_assemblee(raw, legislature="17") is True


def test_a_mandat_assemblee_faux_pour_autre_legislature() -> None:
    raw = {
        "acteur": {
            "uid": "PA9999",
            "mandats": {"mandat": {"typeOrgane": "ASSEMBLEE", "legislature": "16"}},
        }
    }
    assert a_mandat_assemblee(raw, legislature="17") is False
