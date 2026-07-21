"""Schéma de réponse pour le endpoint de santé applicative."""

from datetime import datetime

from pydantic import BaseModel


class HealthOut(BaseModel):
    """État de santé de l'application et de ses dépendances directes."""

    statut: str
    base_de_donnees: bool
    redis: bool
    derniere_collecte: datetime | None
