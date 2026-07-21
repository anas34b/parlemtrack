"""Parsing des fichiers organe.json : ne conserve que les groupes politiques (GP)
rattachés à la législature demandée."""


def parse_groupe(raw: dict, legislature: str = "17") -> dict | None:
    """Normalise un organe brut AN en groupe.

    Retourne None si l'organe n'est pas de type GP, ou s'il est rattaché à
    une autre législature (l'historique AMO30 couvre toutes les législatures
    depuis la 13e, sans filtrer par elle-même). `actif` distingue un groupe
    toujours en activité (`viMoDe.dateFin` absente) d'un groupe dissous ou
    renommé en cours de législature.
    """
    data = raw["organe"]
    if data.get("codeType") != "GP" or data.get("legislature") != legislature:
        return None

    return {
        "id_an": data["uid"],
        "nom": data.get("libelle", ""),
        "nom_court": data.get("libelleAbrev", ""),
        "actif": (data.get("viMoDe") or {}).get("dateFin") is None,
        "couleur": data.get("couleurAssociee"),
    }
