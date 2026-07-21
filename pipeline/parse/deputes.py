"""Parsing des fichiers acteur.json (députés) de l'Assemblée nationale.

L'uid est parfois `{"#text": "PA1234"}`, parfois une chaîne directe.
Le tableau `mandats.mandat` collapse en objet unique s'il n'y a qu'un mandat.
"""


def _as_list(value: object) -> list:
    """Normalise un champ pouvant être un objet unique ou un tableau."""
    if value is None:
        return []
    if isinstance(value, dict):
        return [value]
    return value


def _extract_uid(value: object) -> str:
    """Extrait l'identifiant, que le champ soit une chaîne ou `{"#text": ...}`."""
    if isinstance(value, dict):
        return value["#text"]
    return value


def _dernier_groupe(mandats: list[dict]) -> str | None:
    """Trouve le groupe politique (GP) le plus récent, actif ou non.

    Trié par date de début décroissante : pour un député toujours en
    exercice, c'est nécessairement son groupe actuel ; pour un député
    remplacé, c'est son dernier groupe connu avant la fin de son mandat.
    """
    mandats_gp = [m for m in mandats if m.get("typeOrgane") == "GP"]
    if not mandats_gp:
        return None
    dernier = max(mandats_gp, key=lambda m: m.get("dateDebut") or "")
    return dernier.get("organes", {}).get("organeRef")


def a_mandat_assemblee(raw: dict, legislature: str = "17") -> bool:
    """Indique si l'acteur a eu un mandat de député (ASSEMBLEE) sur la législature donnée."""
    mandats = _as_list(raw["acteur"].get("mandats", {}).get("mandat"))
    return any(
        m.get("typeOrgane") == "ASSEMBLEE" and m.get("legislature") == legislature for m in mandats
    )


def parse_depute(raw: dict, actif: bool = True) -> dict:
    """Normalise un acteur brut AN en dict prêt pour l'upsert.

    `actif` distingue les députés du jeu "en exercice" (AMO10) des députés
    remplacés en cours de législature, retrouvés via l'historique (AMO30).
    """
    data = raw["acteur"]
    ident = data.get("etatCivil", {}).get("ident", {})
    mandats = _as_list(data.get("mandats", {}).get("mandat"))

    return {
        "id_an": _extract_uid(data["uid"]),
        "nom": ident.get("nom", ""),
        "prenom": ident.get("prenom", ""),
        "actif": actif,
        "groupe_id": _dernier_groupe(mandats),
    }
