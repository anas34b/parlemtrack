"""Tests des routes /api/groupes : liste, détail, cohésion, cas d'erreur."""

from backend.app.models import Depute, Groupe, Vote


def test_liste_groupes_vide(client) -> None:
    reponse = client.get("/api/groupes")
    assert reponse.status_code == 200
    assert reponse.json() == []


def test_detail_groupe_404_si_introuvable(client) -> None:
    reponse = client.get("/api/groupes/INEXISTANT")
    assert reponse.status_code == 404


def test_detail_groupe_effectif_et_cohesion(client, db_session) -> None:
    from backend.app.models import Scrutin

    db_session.add(Groupe(id_an="PO1", nom="Groupe A", nom_court="GA", actif=True))
    db_session.add(Depute(id_an="PA1", nom="Dupont", prenom="Jean", actif=True, groupe_id="PO1"))
    db_session.add(Depute(id_an="PA2", nom="Martin", prenom="Alice", actif=True, groupe_id="PO1"))
    db_session.add(
        Scrutin(
            uid="VTA1",
            numero=1,
            date_scrutin="2024-01-01",
            titre="scrutin test",
            type_vote="scrutin public ordinaire",
            sort="adopté",
            nb_pour=2,
            nb_contre=0,
            nb_abstention=0,
            nb_non_votants=0,
        )
    )
    db_session.commit()
    db_session.add(Vote(scrutin_uid="VTA1", depute_id="PA1", position="pour", par_delegation=False))
    db_session.add(Vote(scrutin_uid="VTA1", depute_id="PA2", position="pour", par_delegation=False))
    db_session.commit()

    reponse = client.get("/api/groupes/PO1")

    assert reponse.status_code == 200
    corps = reponse.json()
    assert corps["effectif"] == 2
    assert corps["cohesion_moyenne"] == 1.0
