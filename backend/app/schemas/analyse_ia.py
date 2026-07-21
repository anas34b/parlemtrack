"""Schéma de réponse pour l'analyse IA neutre d'un scrutin."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


class AnalyseIAOut(BaseModel):
    """Analyse factuelle générée par Mistral, stockée définitivement (Phase 3)."""

    model_config = ConfigDict(from_attributes=True)

    resume_factuel: str
    arguments_pour: list[str]
    arguments_contre: list[str]
    coherence_macro: Literal["aligne", "mitige", "contradictoire"]
    indicateurs_ref: list[str]
    modele_utilise: str
    genere_le: datetime
