"""Enveloppe de pagination générique pour les listes paginées de l'API."""

from pydantic import BaseModel


class Page[T](BaseModel):
    """Page de résultats avec métadonnées de pagination."""

    items: list[T]
    total: int
    page: int
    taille_page: int
