"""Schémas de réponse pour les scrutins."""

from datetime import date

from pydantic import BaseModel, ConfigDict

from backend.app.schemas.analyse_ia import AnalyseIAOut


class ScrutinOut(BaseModel):
    """Scrutin, tel que listé dans le fil d'actualité."""

    model_config = ConfigDict(from_attributes=True)

    uid: str
    numero: int
    date_scrutin: date
    titre: str
    type_vote: str
    sort: str
    nb_pour: int
    nb_contre: int
    nb_abstention: int
    nb_non_votants: int
    lien_an: str | None


class VoteParGroupeOut(BaseModel):
    """Décompte des positions de vote d'un groupe sur un scrutin donné."""

    groupe_id: str
    groupe_nom: str
    pour: int
    contre: int
    abstention: int
    non_votant: int


class ScrutinDetail(ScrutinOut):
    """Détail complet d'un scrutin : votes par groupe et analyse IA si disponible."""

    dossier_ref: str | None
    votes_par_groupe: list[VoteParGroupeOut]
    analyse_ia: AnalyseIAOut | None
