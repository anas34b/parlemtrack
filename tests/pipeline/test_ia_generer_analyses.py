"""Tests de l'orchestration de génération des analyses IA : sélection et lot."""

from unittest.mock import patch

import pytest

from backend.app.models import AnalyseIA
from pipeline.ia.generer_analyses import generer_lot, scrutins_sans_analyse
from pipeline.store.upsert import inserer_analyse_ia, upsert_depute, upsert_groupe, upsert_scrutin


def _scrutin_data(**overrides: object) -> dict:
    data = {
        "uid": "VTA1",
        "numero": 1,
        "date_scrutin": "2024-07-20",
        "titre": "scrutin de test",
        "type_vote": "scrutin public ordinaire",
        "sort": "adopté",
        "nb_pour": 1,
        "nb_contre": 0,
        "nb_abstention": 0,
        "nb_non_votants": 0,
        "dossier_ref": None,
        "lien_an": "https://example.org/1",
        "votes": [],
    }
    data.update(overrides)
    return data


def _analyse_ok() -> dict:
    return {
        "resume_factuel": "résumé",
        "arguments_pour": ["a"],
        "arguments_contre": ["b"],
        "coherence_macro": "aligne",
        "indicateurs_ref": ["INSEE"],
        "modele_utilise": "mistral-large-latest",
        "tokens_utilises": 100,
    }


def test_scrutins_sans_analyse_exclut_les_deja_analyses(db_session) -> None:
    upsert_scrutin(db_session, _scrutin_data(uid="VTA1", numero=1))
    upsert_scrutin(db_session, _scrutin_data(uid="VTA2", numero=2, date_scrutin="2024-07-21"))
    db_session.flush()
    inserer_analyse_ia(db_session, "VTA1", _analyse_ok())
    db_session.flush()

    resultat = scrutins_sans_analyse(db_session)

    assert resultat == ["VTA2"]


def test_scrutins_sans_analyse_respecte_la_limite(db_session) -> None:
    for i in range(3):
        upsert_scrutin(db_session, _scrutin_data(uid=f"VTA{i}", numero=i, date_scrutin=f"2024-07-{20 + i}"))
    db_session.flush()

    resultat = scrutins_sans_analyse(db_session, limite=2)

    assert len(resultat) == 2


def test_scrutins_sans_analyse_filtre_par_type_vote(db_session) -> None:
    upsert_scrutin(db_session, _scrutin_data(uid="VTA1", numero=1, type_vote="scrutin public solennel"))
    upsert_scrutin(db_session, _scrutin_data(uid="VTA2", numero=2, type_vote="scrutin public ordinaire"))
    db_session.flush()

    resultat = scrutins_sans_analyse(db_session, type_vote="scrutin public solennel")

    assert resultat == ["VTA1"]


def test_generer_lot_genere_et_stocke(db_session) -> None:
    groupe = {"id_an": "PO1", "nom": "Groupe A", "nom_court": "GA", "actif": True, "couleur": None}
    depute = {"id_an": "PA1", "nom": "Dupont", "prenom": "Jean", "actif": True, "groupe_id": "PO1"}
    upsert_groupe(db_session, groupe)
    upsert_depute(db_session, depute)
    upsert_scrutin(
        db_session,
        _scrutin_data(votes=[{"depute_id": "PA1", "position": "pour", "par_delegation": False}]),
    )
    db_session.commit()

    with patch("pipeline.ia.generer_analyses.generer_analyse", return_value=_analyse_ok()):
        resultat = generer_lot(db_session, ["VTA1"])

    assert resultat["nb_generees"] == 1
    assert resultat["nb_erreurs"] == 0
    assert resultat["tokens_totaux"] == 100
    assert resultat["cout_estime"] == pytest.approx(0.0006)
    assert db_session.get(AnalyseIA, "VTA1").resume_factuel == "résumé"


def test_generer_lot_erreur_isolee_ne_bloque_pas_le_lot(db_session) -> None:
    upsert_scrutin(db_session, _scrutin_data(uid="VTA1", numero=1))
    upsert_scrutin(db_session, _scrutin_data(uid="VTA2", numero=2, date_scrutin="2024-07-21"))
    db_session.commit()

    with (
        patch(
            "pipeline.ia.generer_analyses.generer_analyse",
            side_effect=[Exception("échec réseau"), _analyse_ok()],
        ),
        patch("pipeline.ia.generer_analyses.time.sleep"),
    ):
        resultat = generer_lot(db_session, ["VTA1", "VTA2"])

    assert resultat["nb_generees"] == 1
    assert resultat["nb_erreurs"] == 1
    assert db_session.get(AnalyseIA, "VTA1") is None
    assert db_session.get(AnalyseIA, "VTA2") is not None
