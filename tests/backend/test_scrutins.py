"""Tests des routes /api/scrutins : liste filtrée, détail, cas d'erreur."""

from backend.app.models import Depute, Groupe, Scrutin, Vote


def _creer_scrutin(db_session, uid: str, titre: str, date_scrutin: str, numero: int = 1) -> None:
    db_session.add(
        Scrutin(
            uid=uid,
            numero=numero,
            date_scrutin=date_scrutin,
            titre=titre,
            type_vote="scrutin public ordinaire",
            sort="adopté",
            nb_pour=10,
            nb_contre=5,
            nb_abstention=1,
            nb_non_votants=0,
            lien_an=f"https://www.assemblee-nationale.fr/dyn/17/scrutins/{numero}",
        )
    )
    db_session.commit()


def test_liste_scrutins_vide(client) -> None:
    reponse = client.get("/api/scrutins")

    assert reponse.status_code == 200
    corps = reponse.json()
    assert corps["items"] == []
    assert corps["total"] == 0


def test_liste_scrutins_pagination(client, db_session) -> None:
    _creer_scrutin(db_session, "VTA1", "premier scrutin", "2024-01-01", numero=1)
    _creer_scrutin(db_session, "VTA2", "second scrutin", "2024-01-02", numero=2)

    reponse = client.get("/api/scrutins?taille_page=1&page=1")

    assert reponse.status_code == 200
    corps = reponse.json()
    assert len(corps["items"]) == 1
    assert corps["total"] == 2
    assert corps["items"][0]["uid"] == "VTA2"  # tri par date décroissante


def test_liste_scrutins_recherche_texte(client, db_session) -> None:
    _creer_scrutin(db_session, "VTA1", "loi sur le budget", "2024-01-01")
    _creer_scrutin(db_session, "VTA2", "loi sur la santé", "2024-01-02")

    reponse = client.get("/api/scrutins?q=budget")

    corps = reponse.json()
    assert corps["total"] == 1
    assert corps["items"][0]["uid"] == "VTA1"


def test_liste_scrutins_page_invalide_422(client) -> None:
    reponse = client.get("/api/scrutins?page=0")
    assert reponse.status_code == 422


def test_detail_scrutin_404_si_introuvable(client) -> None:
    reponse = client.get("/api/scrutins/INEXISTANT")
    assert reponse.status_code == 404


def test_detail_scrutin_votes_par_groupe(client, db_session) -> None:
    _creer_scrutin(db_session, "VTA1", "scrutin test", "2024-01-01")
    db_session.add(Groupe(id_an="PO1", nom="Groupe A", nom_court="GA", actif=True))
    db_session.add(Depute(id_an="PA1", nom="Dupont", prenom="Jean", actif=True, groupe_id="PO1"))
    db_session.commit()
    db_session.add(Vote(scrutin_uid="VTA1", depute_id="PA1", position="pour", par_delegation=False))
    db_session.commit()

    reponse = client.get("/api/scrutins/VTA1")

    assert reponse.status_code == 200
    corps = reponse.json()
    assert corps["votes_par_groupe"] == [
        {"groupe_id": "PO1", "groupe_nom": "Groupe A", "pour": 1, "contre": 0, "abstention": 0, "non_votant": 0}
    ]
    assert corps["analyse_ia"] is None
