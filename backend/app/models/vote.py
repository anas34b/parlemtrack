"""Position de vote d'un député sur un scrutin (table de jonction)."""

from sqlalchemy import Boolean, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.models.base import Base


class Vote(Base):
    __tablename__ = "votes"
    __table_args__ = (UniqueConstraint("scrutin_uid", "depute_id", name="uq_scrutin_depute"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    scrutin_uid: Mapped[str] = mapped_column(
        ForeignKey("scrutins.uid"), index=True
    )
    depute_id: Mapped[str] = mapped_column(
        ForeignKey("deputes.id_an"), index=True
    )
    position: Mapped[str] = mapped_column(String(30))
    par_delegation: Mapped[bool] = mapped_column(Boolean, default=False)
