"""Groupe politique de l'Assemblée nationale, actif ou dissous en cours de législature."""

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.models.base import Base


class Groupe(Base):
    __tablename__ = "groupes"

    id_an: Mapped[str] = mapped_column(String(20), primary_key=True)
    nom: Mapped[str] = mapped_column(String(200))
    nom_court: Mapped[str] = mapped_column(String(50))
    actif: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    couleur: Mapped[str | None] = mapped_column(String(7), nullable=True)
