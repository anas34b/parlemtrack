"""Tests de l'intégration Datan : parsing CSV et mise à jour des scores existants."""

from unittest.mock import Mock, patch

from pipeline.collect.datan import mettre_a_jour_scores, parse_ligne_datan, recuperer_scores_datan
from pipeline.store.upsert import upsert_depute


def test_parse_ligne_datan_champs_nominaux() -> None:
    ligne = {"id": "PA1008", "scoreParticipation": "0.06", "scoreLoyaute": "0.914", "scoreMajorite": "0.0"}
    resultat = parse_ligne_datan(ligne)

    assert resultat["id_an"] == "PA1008"
    assert resultat["score_participation"] == 0.06
    assert resultat["score_loyaute"] == 0.914


def test_parse_ligne_datan_champ_vide_donne_none() -> None:
    ligne = {"id": "PA1008", "scoreParticipation": "", "scoreLoyaute": "0.9", "scoreMajorite": "0.0"}
    resultat = parse_ligne_datan(ligne)
    assert resultat["score_participation"] is None


def test_recuperer_scores_datan_resout_url_puis_parse_le_csv() -> None:
    """L'URL du CSV est horodatée et change à chaque republication (BUG-005) : elle est
    résolue dynamiquement via l'API data.gouv.fr plutôt que codée en dur."""
    reponse_api = Mock()
    reponse_api.json.return_value = {
        "resources": [{"format": "csv", "url": "https://static.data.gouv.fr/resources/x/deputes-active.csv"}]
    }
    reponse_api.raise_for_status = Mock()

    reponse_csv = Mock()
    reponse_csv.text = "id,scoreParticipation,scoreLoyaute,scoreMajorite\nPA1,0.5,0.8,0.1\n"
    reponse_csv.raise_for_status = Mock()

    with patch("pipeline.collect.datan.requests.get", side_effect=[reponse_api, reponse_csv]) as mock_get:
        resultat = recuperer_scores_datan()

    assert mock_get.call_args_list[1].args[0] == "https://static.data.gouv.fr/resources/x/deputes-active.csv"
    assert resultat == [{"id_an": "PA1", "score_participation": 0.5, "score_loyaute": 0.8, "score_majorite": 0.1}]


def test_mettre_a_jour_scores_ne_cree_aucun_depute(db_session) -> None:
    upsert_depute(db_session, {"id_an": "PA1", "nom": "Dupont", "prenom": "Jean", "groupe_id": None})
    db_session.flush()

    scores = [
        {"id_an": "PA1", "score_participation": 0.5, "score_loyaute": 0.8, "score_majorite": 0.1},
        {"id_an": "PA_INCONNU", "score_participation": 0.1, "score_loyaute": 0.1, "score_majorite": 0.1},
    ]
    nb_mis_a_jour = mettre_a_jour_scores(db_session, scores)
    db_session.flush()

    from backend.app.models import Depute

    assert nb_mis_a_jour == 1
    assert db_session.get(Depute, "PA1").score_participation == 0.5
    assert db_session.query(Depute).count() == 1
