"""Métadonnées HTTP (ETag / Last-Modified) de la dernière collecte par source.

Permet au downloader de sauter un téléchargement si la ressource distante
n'a pas changé depuis la dernière collecte.
"""

from datetime import UTC, datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.models.base import Base


class SourceMeta(Base):
    __tablename__ = "sources_meta"

    source: Mapped[str] = mapped_column(String(50), primary_key=True)
    etag: Mapped[str | None] = mapped_column(String(200), nullable=True)
    last_modified: Mapped[str | None] = mapped_column(String(100), nullable=True)
    derniere_collecte: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
