"""Journal des runs du pipeline de collecte, un enregistrement par exécution."""

from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.models.base import Base


class CollecteLog(Base):
    __tablename__ = "collectes_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date_run: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
    nb_scrutins_traites: Mapped[int] = mapped_column(Integer, default=0)
    nb_nouveaux: Mapped[int] = mapped_column(Integer, default=0)
    nb_analyses_generees: Mapped[int] = mapped_column(Integer, default=0)
    nb_erreurs: Mapped[int] = mapped_column(Integer, default=0)
    duree_s: Mapped[float] = mapped_column(Float, default=0.0)
    statut: Mapped[str] = mapped_column(String(20))
