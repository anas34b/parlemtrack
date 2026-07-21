"""Parsing des fichiers scrutin.json de l'Assemblée nationale.

Un fichier brut = un scrutin. Le format expose plusieurs champs qui sont
tantôt un objet, tantôt un tableau selon leur cardinalité (un seul groupe
ou un seul votant collapse en objet) : on normalise systématiquement.
"""

import logging

logger = logging.getLogger("pipeline.parse.scrutins")

POSITIONS_DECOMPTE = {
    "pours": "pour",
    "contres": "contre",
    "abstentions": "abstention",
    "nonVotants": "nonVotant",
    "nonVotantsVolontaires": "nonVotantVolontaire",
}


def _as_list(value: object) -> list:
    """Normalise un champ pouvant être un objet unique ou un tableau."""
    if value is None:
        return []
    if isinstance(value, dict):
        return [value]
    return value


def _to_int(value: object, defaut: int = 0) -> int:
    """Convertit une valeur AN (chaîne numérique) en entier, défensivement."""
    if value is None:
        return defaut
    try:
        return int(value)
    except (TypeError, ValueError):
        return defaut


def _to_bool(value: object) -> bool:
    """Convertit une chaîne `"true"/"false"` AN en booléen."""
    return str(value).lower() == "true"


def _extract_dossier_ref(objet: dict) -> str | None:
    """Extrait la référence de dossier législatif, objet ou chaîne selon les scrutins."""
    dossier = objet.get("dossierLegislatif")
    if isinstance(dossier, dict):
        return dossier.get("dossierRef")
    return dossier


def _parse_votes(ventilation: dict | None) -> list[dict]:
    """Extrait la liste des votes individuels depuis `ventilationVotes`."""
    if not ventilation:
        return []
    groupes = _as_list(ventilation.get("organe", {}).get("groupes", {}).get("groupe"))
    votes = []
    for groupe in groupes:
        decompte = (groupe.get("vote") or {}).get("decompteNominatif") or {}
        for cle_decompte, position in POSITIONS_DECOMPTE.items():
            bloc = decompte.get(cle_decompte)
            if not bloc:
                continue
            for votant in _as_list(bloc.get("votant")):
                votes.append(
                    {
                        "depute_id": votant.get("acteurRef"),
                        "position": position,
                        "par_delegation": _to_bool(votant.get("parDelegation")),
                    }
                )
    return votes


def parse_scrutin(raw: dict) -> dict:
    """Normalise un scrutin brut AN en dict prêt pour l'upsert.

    Le champ `syntheseVote` peut être absent (scrutins procéduraux) :
    on retombe alors sur des décomptes à zéro avec un WARNING loggé.
    """
    data = raw["scrutin"]
    synthese = data.get("syntheseVote")
    if synthese is None:
        logger.warning("syntheseVote absente pour le scrutin %s", data.get("uid"))
        decompte = {}
    else:
        decompte = synthese.get("decompte", {}) or {}

    objet = data.get("objet") or {}

    return {
        "uid": data["uid"],
        "numero": _to_int(data.get("numero")),
        "date_scrutin": data["dateScrutin"],
        "titre": data.get("titre", ""),
        "type_vote": data.get("typeVote", {}).get("libelleTypeVote", ""),
        "sort": data.get("sort", {}).get("code", ""),
        "nb_pour": _to_int(decompte.get("pour")),
        "nb_contre": _to_int(decompte.get("contre")),
        "nb_abstention": _to_int(decompte.get("abstentions")),
        "nb_non_votants": _to_int(decompte.get("nonVotants")),
        "dossier_ref": _extract_dossier_ref(objet),
        "lien_an": f"https://www.assemblee-nationale.fr/dyn/17/scrutins/{data['uid']}",
        "votes": _parse_votes(data.get("ventilationVotes")),
    }
