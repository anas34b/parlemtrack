"""Scrutin public de l'Assemblée nationale."""

from datetime import date

from sqlalchemy import Date, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.models.base import Base


class Scrutin(Base):
    __tablename__ = "scrutins"

    uid: Mapped[str] = mapped_column(String(30), primary_key=True)
    numero: Mapped[int] = mapped_column(Integer)
    date_scrutin: Mapped[date] = mapped_column(Date, index=True)
    titre: Mapped[str] = mapped_column(String(500))
    type_vote: Mapped[str] = mapped_column(String(100))
    sort: Mapped[str] = mapped_column(String(50))
    nb_pour: Mapped[int] = mapped_column(Integer, default=0)
    nb_contre: Mapped[int] = mapped_column(Integer, default=0)
    nb_abstention: Mapped[int] = mapped_column(Integer, default=0)
    nb_non_votants: Mapped[int] = mapped_column(Integer, default=0)
    dossier_ref: Mapped[str | None] = mapped_column(String(200), nullable=True)
    lien_an: Mapped[str | None] = mapped_column(String(500), nullable=True)
