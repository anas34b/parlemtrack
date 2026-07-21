"""Tests des fonctions d'upsert : idempotence, aucune suppression, pas de doublon."""

from backend.app.models import Depute, Groupe, Scrutin, Vote
from pipeline.store.upsert import desactiver_deputes_absents, upsert_depute, upsert_groupe, upsert_scrutin


def _scrutin_data(**overrides: object) -> dict:
    data = {
        "uid": "VTANR5L17V0001",
        "numero": 1,
        "date_scrutin": "2024-07-20",
        "titre": "scrutin de test",
        "type_vote": "scrutin public ordinaire",
        "sort": "adopté",
        "nb_pour": 10,
        "nb_contre": 5,
        "nb_abstention": 1,
        "nb_non_votants": 0,
        "dossier_ref": None,
        "lien_an": "https://example.org/scrutin/1",
        "votes": [],
    }
    data.update(overrides)
    return data


def test_upsert_groupe_insertion_puis_mise_a_jour(db_session) -> None:
    upsert_groupe(db_session, {"id_an": "PO1", "nom": "Groupe A", "nom_court": "GA", "couleur": "#000000"})
    upsert_groupe(db_session, {"id_an": "PO1", "nom": "Groupe A renommé", "nom_court": "GA", "couleur": "#111111"})
    db_session.flush()

    groupe = db_session.get(Groupe, "PO1")
    assert groupe.nom == "Groupe A renommé"
    assert db_session.query(Groupe).count() == 1


def test_upsert_depute_insertion_puis_mise_a_jour(db_session) -> None:
    upsert_depute(db_session, {"id_an": "PA1", "nom": "Dupont", "prenom": "Jean", "groupe_id": None})
    upsert_depute(db_session, {"id_an": "PA1", "nom": "Dupont", "prenom": "Jean", "groupe_id": None})
    db_session.flush()

    assert db_session.query(Depute).count() == 1


def test_desactiver_deputes_absents_bascule_et_epargne_les_presents(db_session) -> None:
    upsert_depute(db_session, {"id_an": "PA1", "nom": "Reste", "prenom": "Ana", "actif": True, "groupe_id": None})
    upsert_depute(db_session, {"id_an": "PA2", "nom": "Parti", "prenom": "Marc", "actif": True, "groupe_id": None})
    db_session.flush()

    desactives = desactiver_deputes_absents(db_session, ids_actifs_courants={"PA1"})
    db_session.flush()

    assert [d.id_an for d in desactives] == ["PA2"]
    assert db_session.get(Depute, "PA1").actif is True
    assert db_session.get(Depute, "PA2").actif is False
    assert db_session.query(Depute).count() == 2  # jamais de suppression


def test_upsert_scrutin_signale_nouveau_puis_existant(db_session) -> None:
    est_nouveau_1 = upsert_scrutin(db_session, _scrutin_data())
    db_session.flush()
    est_nouveau_2 = upsert_scrutin(db_session, _scrutin_data())
    db_session.flush()

    assert est_nouveau_1 is True
    assert est_nouveau_2 is False
    assert db_session.query(Scrutin).count() == 1


def test_upsert_scrutin_vote_depute_inconnu_ignore_sans_lever(db_session) -> None:
    """Un vote référençant un député absent du jeu actifs est ignoré, pas une erreur fatale."""
    upsert_depute(db_session, {"id_an": "PA1", "nom": "Dupont", "prenom": "Jean", "groupe_id": None})
    db_session.flush()

    votes = [
        {"depute_id": "PA1", "position": "pour", "par_delegation": False},
        {"depute_id": "PA_INCONNU", "position": "contre", "par_delegation": False},
    ]
    upsert_scrutin(db_session, _scrutin_data(votes=votes))
    db_session.flush()

    assert db_session.query(Vote).count() == 1


def test_upsert_scrutin_avec_votes_sans_doublon(db_session) -> None:
    upsert_depute(db_session, {"id_an": "PA1", "nom": "Dupont", "prenom": "Jean", "groupe_id": None})
    db_session.flush()

    votes = [{"depute_id": "PA1", "position": "pour", "par_delegation": False}]
    upsert_scrutin(db_session, _scrutin_data(votes=list(votes)))
    db_session.flush()
    upsert_scrutin(db_session, _scrutin_data(votes=list(votes)))
    db_session.flush()

    assert db_session.query(Vote).count() == 1
