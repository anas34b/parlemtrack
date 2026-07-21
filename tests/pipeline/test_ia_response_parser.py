"""Tests du parsing de la réponse Mistral : JSON valide, avec fences, invalide."""

import json

import pytest

from pipeline.ia.response_parser import ReponseIAInvalide, parse_reponse_ia


def _donnees_valides() -> dict:
    return {
        "resume_factuel": "Le texte modifie X.",
        "arguments_pour": ["argument 1"],
        "arguments_contre": ["argument 1"],
        "coherence_macro": "aligne",
        "indicateurs_ref": ["INSEE"],
    }


def test_parse_json_valide() -> None:
    resultat = parse_reponse_ia(json.dumps(_donnees_valides()))
    assert resultat["coherence_macro"] == "aligne"


def test_parse_json_avec_fences_markdown() -> None:
    texte = f"```json\n{json.dumps(_donnees_valides())}\n```"
    resultat = parse_reponse_ia(texte)
    assert resultat["resume_factuel"] == "Le texte modifie X."


def test_parse_json_avec_fences_sans_langage() -> None:
    texte = f"```\n{json.dumps(_donnees_valides())}\n```"
    resultat = parse_reponse_ia(texte)
    assert resultat["coherence_macro"] == "aligne"


def test_parse_json_invalide_leve_erreur_propre() -> None:
    with pytest.raises(ReponseIAInvalide, match="JSON invalide"):
        parse_reponse_ia("ceci n'est pas du JSON")


def test_parse_json_cles_manquantes_leve_erreur() -> None:
    with pytest.raises(ReponseIAInvalide, match="clés manquantes"):
        parse_reponse_ia(json.dumps({"resume_factuel": "x"}))


def test_parse_json_coherence_macro_invalide_leve_erreur() -> None:
    donnees = _donnees_valides()
    donnees["coherence_macro"] = "positif"
    with pytest.raises(ReponseIAInvalide, match="coherence_macro invalide"):
        parse_reponse_ia(json.dumps(donnees))
