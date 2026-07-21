"""Schéma de réponse pour les titres d'actualité presse (cache Redis)."""

from pydantic import BaseModel


class ActualiteOut(BaseModel):
    """Un titre de presse issu d'un flux RSS suivi."""

    source: str
    titre: str
    lien: str
    date_publication: str
