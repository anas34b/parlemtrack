"""Tests du parser de scrutins, cas limites du format AN."""

import json
from pathlib import Path

from pipeline.parse.scrutins import parse_scrutin

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


def _load(nom: str) -> dict:
    return json.loads((FIXTURES / nom).read_text(encoding="utf-8"))


def test_scrutin_nominal_champs_de_base() -> None:
    resultat = parse_scrutin(_load("scrutin_nominal.json"))

    assert resultat["uid"] == "VTANR5L17V1144"
    assert resultat["numero"] == 1144
    assert resultat["date_scrutin"] == "2025-03-24"
    assert resultat["sort"] == "adopté"
    assert resultat["nb_pour"] == 63
    assert resultat["nb_contre"] == 30
    assert resultat["nb_abstention"] == 9
    assert resultat["nb_non_votants"] == 2
    assert resultat["dossier_ref"] == "DLR5L17N12345"


def test_scrutin_nominal_votes_extraits_et_normalises() -> None:
    resultat = parse_scrutin(_load("scrutin_nominal.json"))
    votes = {v["depute_id"]: v for v in resultat["votes"]}

    assert len(resultat["votes"]) == 6
    assert votes["PA796118"]["position"] == "pour"
    assert votes["PA796118"]["par_delegation"] is False
    assert votes["PA841487"]["par_delegation"] is True
    assert votes["PA720668"]["position"] == "contre"
    assert votes["PA793548"]["position"] == "abstention"
    assert votes["PA606507"]["position"] == "nonVotant"
    assert votes["PA608016"]["position"] == "nonVotantVolontaire"


def test_scrutin_groupe_et_votant_uniques_normalises_en_liste() -> None:
    """Piège AN : un seul groupe ou un seul votant devient un objet, pas un tableau."""
    resultat = parse_scrutin(_load("scrutin_groupe_unique.json"))

    assert len(resultat["votes"]) == 1
    assert resultat["votes"][0]["depute_id"] == "PA796118"
    assert resultat["votes"][0]["position"] == "pour"


def test_scrutin_sans_synthese_vote_valeurs_par_defaut() -> None:
    """Piège AN : syntheseVote peut être absente sur les scrutins procéduraux."""
    resultat = parse_scrutin(_load("scrutin_sans_synthese.json"))

    assert resultat["nb_pour"] == 0
    assert resultat["nb_contre"] == 0
    assert resultat["votes"] == []


def test_scrutin_numero_chaine_convertie_en_entier() -> None:
    resultat = parse_scrutin(_load("scrutin_nominal.json"))
    assert isinstance(resultat["numero"], int)


def test_scrutin_dossier_legislatif_objet_donne_la_reference() -> None:
    """Piège AN : `objet.dossierLegislatif` est parfois un objet, parfois une chaîne."""
    resultat = parse_scrutin(_load("scrutin_dossier_objet.json"))
    assert resultat["dossier_ref"] == "DLR5L17N54083"
