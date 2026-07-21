"""Schémas de réponse pour les groupes politiques."""

from pydantic import BaseModel, ConfigDict


class GroupeOut(BaseModel):
    """Groupe politique, tel que listé ou référencé depuis un autre objet."""

    model_config = ConfigDict(from_attributes=True)

    id_an: str
    nom: str
    nom_court: str
    actif: bool
    couleur: str | None


class GroupeDetail(GroupeOut):
    """Fiche détaillée d'un groupe : effectif et cohésion des votes."""

    effectif: int
    cohesion_moyenne: float | None
