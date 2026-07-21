"""Schémas de réponse pour les députés."""

from datetime import date

from pydantic import BaseModel, ConfigDict

from backend.app.schemas.groupe import GroupeOut
from backend.app.schemas.pagination import Page


class DeputeOut(BaseModel):
    """Député, tel que listé dans l'annuaire."""

    model_config = ConfigDict(from_attributes=True)

    id_an: str
    nom: str
    prenom: str
    actif: bool
    departement: str | None
    circonscription: str | None
    groupe: GroupeOut | None = None


class VoteHistoriqueOut(BaseModel):
    """Une ligne de l'historique de vote d'un député, avec le contexte du scrutin."""

    model_config = ConfigDict(from_attributes=True)

    scrutin_uid: str
    scrutin_titre: str
    scrutin_date: date
    position: str
    par_delegation: bool


class DeputeDetail(DeputeOut):
    """Fiche complète d'un député : scores Datan."""

    score_participation: float | None
    score_loyaute: float | None
    score_majorite: float | None


class DeputeFiche(BaseModel):
    """Réponse complète de la fiche député : identité + historique de votes paginé."""

    depute: DeputeDetail
    historique_votes: Page[VoteHistoriqueOut]
