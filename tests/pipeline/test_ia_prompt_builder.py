"""Tests du prompt builder : contenu injecté dans le prompt utilisateur."""

from pipeline.ia.prompt_builder import PROMPT_SYSTEME, build_user_prompt


def _scrutin() -> dict:
    return {
        "titre": "l'ensemble de la proposition de loi relative au droit à l'aide à mourir",
        "date_scrutin": "2026-07-15",
        "type_vote": "scrutin public solennel",
        "sort": "adopté",
        "nb_pour": 305,
        "nb_contre": 199,
        "nb_abstention": 15,
        "nb_non_votants": 2,
        "votes_par_groupe": [
            {"groupe_nom": "Groupe A", "pour": 100, "contre": 0, "abstention": 0, "non_votant": 0},
            {"groupe_nom": "Groupe B", "pour": 0, "contre": 80, "abstention": 5, "non_votant": 1},
        ],
    }


def test_prompt_systeme_contient_les_interdictions() -> None:
    assert "prendre parti" in PROMPT_SYSTEME
    assert "JSON strict" in PROMPT_SYSTEME
    assert "aligne|mitige|contradictoire" in PROMPT_SYSTEME


def test_prompt_systeme_interdit_les_statistiques_chiffrees() -> None:
    assert "statistiques chiffrées précises" in PROMPT_SYSTEME
    assert "reste qualitatif" in PROMPT_SYSTEME


def test_prompt_utilisateur_injecte_le_titre_et_la_date() -> None:
    prompt = build_user_prompt(_scrutin())
    assert "l'ensemble de la proposition de loi relative au droit à l'aide à mourir" in prompt
    assert "2026-07-15" in prompt
    assert "scrutin public solennel" in prompt
    assert "adopté" in prompt


def test_prompt_utilisateur_injecte_le_decompte_des_voix() -> None:
    prompt = build_user_prompt(_scrutin())
    assert "305 pour" in prompt
    assert "199 contre" in prompt


def test_prompt_utilisateur_injecte_les_positions_par_groupe() -> None:
    prompt = build_user_prompt(_scrutin())
    assert "Groupe A : 100 pour" in prompt
    assert "Groupe B : 0 pour, 80 contre, 5 abstention(s), 1 non-votant(s)" in prompt


def test_prompt_utilisateur_sans_votes_par_groupe() -> None:
    scrutin = _scrutin()
    scrutin["votes_par_groupe"] = []
    prompt = build_user_prompt(scrutin)
    assert "Positions par groupe :\n" in prompt
