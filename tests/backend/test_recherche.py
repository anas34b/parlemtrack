"""Tests de la route /api/recherche."""

from backend.app.models import Depute, Groupe, Scrutin


def test_recherche_sans_q_422(client) -> None:
    reponse = client.get("/api/recherche")
    assert reponse.status_code == 422


def test_recherche_trouve_depute_groupe_et_scrutin(client, db_session) -> None:
    db_session.add(Groupe(id_an="PO1", nom="Groupe Budget", nom_court="GB", actif=True))
    db_session.add(Depute(id_an="PA1", nom="Budgetier", prenom="Jean", actif=True, groupe_id=None))
    db_session.add(
        Scrutin(
            uid="VTA1",
            numero=1,
            date_scrutin="2024-01-01",
            titre="loi de finances budget",
            type_vote="scrutin public ordinaire",
            sort="adopté",
            nb_pour=1,
            nb_contre=0,
            nb_abstention=0,
            nb_non_votants=0,
        )
    )
    db_session.commit()

    reponse = client.get("/api/recherche?q=budget")

    corps = reponse.json()
    assert len(corps["deputes"]) == 1
    assert len(corps["groupes"]) == 1
    assert len(corps["scrutins"]) == 1


def test_recherche_aucun_resultat(client) -> None:
    reponse = client.get("/api/recherche?q=zzzzz")
    corps = reponse.json()
    assert corps == {"deputes": [], "groupes": [], "scrutins": []}
