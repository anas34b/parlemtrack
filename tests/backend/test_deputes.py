"""Tests des routes /api/deputes : annuaire filtré, fiche, cas d'erreur."""

from backend.app.models import Depute, Groupe, Scrutin, Vote


def test_liste_deputes_vide(client) -> None:
    reponse = client.get("/api/deputes")
    assert reponse.status_code == 200
    assert reponse.json()["items"] == []


def test_liste_deputes_filtre_actif(client, db_session) -> None:
    db_session.add(Depute(id_an="PA1", nom="Actif", prenom="A", actif=True, groupe_id=None))
    db_session.add(Depute(id_an="PA2", nom="Remplace", prenom="B", actif=False, groupe_id=None))
    db_session.commit()

    reponse = client.get("/api/deputes?actif=true")

    corps = reponse.json()
    assert corps["total"] == 1
    assert corps["items"][0]["id_an"] == "PA1"


def test_liste_deputes_filtre_groupe(client, db_session) -> None:
    db_session.add(Groupe(id_an="PO1", nom="Groupe A", nom_court="GA", actif=True))
    db_session.add(Depute(id_an="PA1", nom="Dupont", prenom="Jean", actif=True, groupe_id="PO1"))
    db_session.add(Depute(id_an="PA2", nom="Martin", prenom="Alice", actif=True, groupe_id=None))
    db_session.commit()

    reponse = client.get("/api/deputes?groupe=PO1")

    corps = reponse.json()
    assert corps["total"] == 1
    assert corps["items"][0]["id_an"] == "PA1"


def test_fiche_depute_404_si_introuvable(client) -> None:
    reponse = client.get("/api/deputes/INEXISTANT")
    assert reponse.status_code == 404


def test_fiche_depute_historique_votes_paginee(client, db_session) -> None:
    db_session.add(Depute(id_an="PA1", nom="Dupont", prenom="Jean", actif=True, groupe_id=None))
    db_session.add(
        Scrutin(
            uid="VTA1",
            numero=1,
            date_scrutin="2024-01-01",
            titre="scrutin test",
            type_vote="scrutin public ordinaire",
            sort="adopté",
            nb_pour=1,
            nb_contre=0,
            nb_abstention=0,
            nb_non_votants=0,
        )
    )
    db_session.commit()
    db_session.add(Vote(scrutin_uid="VTA1", depute_id="PA1", position="pour", par_delegation=False))
    db_session.commit()

    reponse = client.get("/api/deputes/PA1")

    assert reponse.status_code == 200
    corps = reponse.json()
    assert corps["depute"]["id_an"] == "PA1"
    assert corps["historique_votes"]["total"] == 1
    assert corps["historique_votes"]["items"][0]["scrutin_uid"] == "VTA1"


def test_liste_deputes_page_invalide_422(client) -> None:
    reponse = client.get("/api/deputes?taille_page=0")
    assert reponse.status_code == 422
