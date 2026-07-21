"""Tests du client Mistral : appel mocké, retries avec backoff, comptage tokens."""

import json
from unittest.mock import MagicMock, patch

import pytest

from backend.app.core.config import Settings
from pipeline.ia.mistral_client import generer_analyse

SETTINGS = Settings(database_url="x", redis_url="x", mistral_api_key="fake", mistral_model="mistral-large-latest")


def _scrutin() -> dict:
    return {
        "uid": "VTA1",
        "titre": "titre test",
        "date_scrutin": "2026-01-01",
        "type_vote": "scrutin public ordinaire",
        "sort": "adopté",
        "nb_pour": 1,
        "nb_contre": 0,
        "nb_abstention": 0,
        "nb_non_votants": 0,
        "votes_par_groupe": [],
    }


def _reponse_ok() -> MagicMock:
    contenu = json.dumps(
        {
            "resume_factuel": "résumé",
            "arguments_pour": ["a"],
            "arguments_contre": ["b"],
            "coherence_macro": "aligne",
            "indicateurs_ref": ["INSEE"],
        }
    )
    reponse = MagicMock()
    reponse.choices = [MagicMock(message=MagicMock(content=contenu))]
    reponse.usage = MagicMock(total_tokens=123)
    return reponse


def test_generer_analyse_nominal() -> None:
    client_mock = MagicMock()
    client_mock.chat.complete.return_value = _reponse_ok()

    with patch("pipeline.ia.mistral_client.Mistral", return_value=client_mock):
        resultat = generer_analyse(_scrutin(), settings=SETTINGS)

    assert resultat["resume_factuel"] == "résumé"
    assert resultat["modele_utilise"] == "mistral-large-latest"
    assert resultat["tokens_utilises"] == 123
    client_mock.chat.complete.assert_called_once()


def test_generer_analyse_retry_puis_succes() -> None:
    client_mock = MagicMock()
    client_mock.chat.complete.side_effect = [ConnectionError("réseau"), _reponse_ok()]

    with (
        patch("pipeline.ia.mistral_client.Mistral", return_value=client_mock),
        patch("pipeline.ia.mistral_client.time.sleep"),
    ):
        resultat = generer_analyse(_scrutin(), settings=SETTINGS)

    assert resultat["tokens_utilises"] == 123
    assert client_mock.chat.complete.call_count == 2


def test_generer_analyse_echec_apres_tous_les_retries() -> None:
    client_mock = MagicMock()
    client_mock.chat.complete.side_effect = ConnectionError("réseau")

    with (
        patch("pipeline.ia.mistral_client.Mistral", return_value=client_mock),
        patch("pipeline.ia.mistral_client.time.sleep"),
        pytest.raises(ConnectionError),
    ):
        generer_analyse(_scrutin(), settings=SETTINGS)

    assert client_mock.chat.complete.call_count == 3
