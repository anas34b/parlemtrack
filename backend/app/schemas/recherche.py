"""Schéma de réponse pour la recherche unifiée député / groupe / scrutin."""

from pydantic import BaseModel

from backend.app.schemas.depute import DeputeOut
from backend.app.schemas.groupe import GroupeOut
from backend.app.schemas.scrutin import ScrutinOut


class RechercheResultat(BaseModel):
    """Résultats de recherche groupés par type d'entité."""

    deputes: list[DeputeOut]
    groupes: list[GroupeOut]
    scrutins: list[ScrutinOut]
