"""Modèles SQLAlchemy — un fichier par table."""

from backend.app.models.analyse_ia import AnalyseIA
from backend.app.models.base import Base
from backend.app.models.collecte_log import CollecteLog
from backend.app.models.depute import Depute
from backend.app.models.groupe import Groupe
from backend.app.models.scrutin import Scrutin
from backend.app.models.source_meta import SourceMeta
from backend.app.models.vote import Vote

__all__ = [
    "AnalyseIA",
    "Base",
    "CollecteLog",
    "Depute",
    "Groupe",
    "Scrutin",
    "SourceMeta",
    "Vote",
]
