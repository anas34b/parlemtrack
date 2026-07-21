"""Analyse IA neutre d'un scrutin, générée une seule fois et stockée définitivement."""

from datetime import UTC, datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.models.base import Base


class AnalyseIA(Base):
    __tablename__ = "analyses_ia"

    scrutin_uid: Mapped[str] = mapped_column(
        ForeignKey("scrutins.uid"), primary_key=True
    )
    resume_factuel: Mapped[str] = mapped_column(Text)
    arguments_pour: Mapped[list] = mapped_column(JSON)
    arguments_contre: Mapped[list] = mapped_column(JSON)
    coherence_macro: Mapped[str] = mapped_column(String(20))
    indicateurs_ref: Mapped[list] = mapped_column(JSON)
    modele_utilise: Mapped[str] = mapped_column(String(50))
    tokens_utilises: Mapped[int] = mapped_column(Integer, default=0)
    genere_le: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
