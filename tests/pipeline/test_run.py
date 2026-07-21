"""Tests des fonctions d'orchestration du pipeline, réseau mocké."""

import json
from unittest.mock import Mock, patch

from backend.app.models import Depute, Groupe, Scrutin
from pipeline.run import _collecter_deputes_et_groupes, _collecter_scrutins
from pipeline.store.upsert import upsert_depute


def _archive_fausse(fichiers: dict[str, dict]) -> Mock:
    archive = Mock()
    archive.namelist.return_value = list(fichiers.keys())
    archive.read.side_effect = lambda nom: json.dumps(fichiers[nom]).encode("utf-8")
    return archive


def _archive_organe_et_acteur(id_an: str, dernier_mandat_gp_fin: str | None) -> Mock:
    return _archive_fausse(
        {
            "json/organe/PO845401.json": {
                "organe": {
                    "uid": "PO845401",
                    "codeType": "GP",
                    "legislature": "17",
                    "libelle": "Groupe A",
                    "libelleAbrev": "GA",
                    "viMoDe": {"dateFin": None},
                }
            },
            "json/acteur/" + id_an + ".json": {
                "acteur": {
                    "uid": id_an,
                    "etatCivil": {"ident": {"nom": "Dupont", "prenom": "Jean"}},
                    "mandats": {
                        "mandat": [
                            {
                                "typeOrgane": "GP",
                                "dateDebut": "2024-07-20",
                                "dateFin": dernier_mandat_gp_fin,
                                "organes": {"organeRef": "PO845401"},
                            },
                            {"typeOrgane": "ASSEMBLEE", "legislature": "17", "dateDebut": "2024-07-20"},
                        ]
                    },
                }
            },
        }
    )


def test_collecter_deputes_et_groupes_sources_inchangees(db_session) -> None:
    with patch("pipeline.run.telecharger_zip", return_value=None):
        resultat = _collecter_deputes_et_groupes(db_session)

    assert resultat == (0, 0, 0)


def test_collecter_deputes_et_groupes_upsert_reel(db_session) -> None:
    archive_actifs = _archive_organe_et_acteur("PA1", dernier_mandat_gp_fin=None)
    with patch("pipeline.run.telecharger_zip", side_effect=[archive_actifs, None]):
        nb_groupes, nb_deputes_actifs, nb_deputes_inactifs = _collecter_deputes_et_groupes(db_session)
    db_session.flush()

    assert (nb_groupes, nb_deputes_actifs, nb_deputes_inactifs) == (1, 1, 0)
    assert db_session.get(Groupe, "PO845401").nom == "Groupe A"
    depute = db_session.get(Depute, "PA1")
    assert depute.groupe_id == "PO845401"
    assert depute.actif is True


def test_collecter_deputes_et_groupes_depute_remplace_insere_inactif(db_session) -> None:
    """Un député présent dans l'historique (AMO30) mais absent des actifs (AMO10)
    est inséré avec actif=False, son dernier groupe connu renseigné (BUG-003)."""
    archive_historique = _archive_organe_et_acteur("PA_REMPLACE", dernier_mandat_gp_fin="2025-01-01")
    with patch("pipeline.run.telecharger_zip", side_effect=[None, archive_historique]):
        nb_groupes, nb_deputes_actifs, nb_deputes_inactifs = _collecter_deputes_et_groupes(db_session)
    db_session.flush()

    assert (nb_groupes, nb_deputes_actifs, nb_deputes_inactifs) == (1, 0, 1)
    depute = db_session.get(Depute, "PA_REMPLACE")
    assert depute.actif is False
    assert depute.groupe_id == "PO845401"


def test_collecter_deputes_et_groupes_bascule_automatiquement_les_deputes_absents(db_session) -> None:
    """Un député actif=true en base qui n'apparaît plus dans le téléchargement AMO10
    courant passe automatiquement à actif=False, sans être supprimé."""
    upsert_depute(
        db_session, {"id_an": "PA_PARTI", "nom": "Ancien", "prenom": "Marc", "actif": True, "groupe_id": None}
    )
    db_session.flush()

    archive_actifs = _archive_organe_et_acteur("PA1", dernier_mandat_gp_fin=None)
    with patch("pipeline.run.telecharger_zip", side_effect=[archive_actifs, None]):
        _collecter_deputes_et_groupes(db_session)
    db_session.flush()

    depute_parti = db_session.get(Depute, "PA_PARTI")
    assert depute_parti is not None
    assert depute_parti.actif is False
    assert db_session.get(Depute, "PA1").actif is True


def test_collecter_deputes_et_groupes_ignore_acteur_sans_mandat_assemblee(db_session) -> None:
    """Un acteur historique sans mandat ASSEMBLEE en législature 17 (ex. sénateur,
    ministre non-parlementaire) n'est pas inséré comme député."""
    archive_historique = _archive_fausse(
        {
            "json/acteur/PA_AUTRE.json": {
                "acteur": {
                    "uid": "PA_AUTRE",
                    "etatCivil": {"ident": {"nom": "Martin", "prenom": "Alice"}},
                    "mandats": {"mandat": {"typeOrgane": "GOUVERNEMENT", "dateDebut": "2024-01-01"}},
                }
            }
        }
    )
    with patch("pipeline.run.telecharger_zip", side_effect=[None, archive_historique]):
        resultat = _collecter_deputes_et_groupes(db_session)
    db_session.flush()

    assert resultat == (0, 0, 0)
    assert db_session.get(Depute, "PA_AUTRE") is None


def test_collecter_scrutins_source_inchangee(db_session) -> None:
    with patch("pipeline.run.telecharger_zip", return_value=None):
        resultat = _collecter_scrutins(db_session)
    assert resultat == (0, 0, 0)


def test_collecter_scrutins_upsert_reel(db_session) -> None:
    scrutin_valide = {
        "scrutin": {
            "uid": "VTANR5L17V1",
            "numero": "1",
            "dateScrutin": "2024-07-20",
            "typeVote": {"libelleTypeVote": "scrutin public ordinaire"},
            "sort": {"code": "adopté"},
            "titre": "test",
            "syntheseVote": {"decompte": {"pour": "1", "contre": "0", "abstentions": "0", "nonVotants": "0"}},
            "ventilationVotes": None,
        }
    }
    fichiers = {"json/VTANR5L17V1.json": scrutin_valide}
    with patch("pipeline.run.telecharger_zip", return_value=_archive_fausse(fichiers)):
        nb_traites, nb_nouveaux, nb_erreurs = _collecter_scrutins(db_session)
    db_session.flush()

    assert nb_traites == 1
    assert nb_nouveaux == 1
    assert nb_erreurs == 0
    assert db_session.get(Scrutin, "VTANR5L17V1") is not None


def test_collecter_scrutins_erreur_de_parsing_loggee_sans_lever(db_session) -> None:
    fichiers = {"json/VTANR5L17V_INVALIDE.json": {"scrutin": {}}}  # pas de uid ni dateScrutin
    with patch("pipeline.run.telecharger_zip", return_value=_archive_fausse(fichiers)):
        nb_traites, nb_nouveaux, nb_erreurs = _collecter_scrutins(db_session)

    assert (nb_traites, nb_nouveaux, nb_erreurs) == (0, 0, 1)
