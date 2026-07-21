"""Député en exercice ou ayant quitté son mandat en cours de législature."""

from sqlalchemy import Boolean, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.models.base import Base
from backend.app.models.groupe import Groupe


class Depute(Base):
    __tablename__ = "deputes"

    id_an: Mapped[str] = mapped_column(String(20), primary_key=True)
    nom: Mapped[str] = mapped_column(String(100))
    prenom: Mapped[str] = mapped_column(String(100))
    actif: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    groupe_id: Mapped[str | None] = mapped_column(
        ForeignKey("groupes.id_an"), nullable=True, index=True
    )
    groupe: Mapped[Groupe | None] = relationship(lazy="joined")
    departement: Mapped[str | None] = mapped_column(String(100), nullable=True)
    circonscription: Mapped[str | None] = mapped_column(String(10), nullable=True)
    score_participation: Mapped[float | None] = mapped_column(Float, nullable=True)
    score_loyaute: Mapped[float | None] = mapped_column(Float, nullable=True)
    score_majorite: Mapped[float | None] = mapped_column(Float, nullable=True)
