"""Journalisation des runs du pipeline et métadonnées HTTP des sources."""

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from backend.app.models import CollecteLog, SourceMeta


def log_collecte(session: Session, **kwargs: object) -> None:
    """Enregistre un run du pipeline dans `collectes_log`."""
    session.add(CollecteLog(**kwargs))


def get_source_meta(session: Session, source: str) -> SourceMeta | None:
    """Retourne l'ETag/Last-Modified connus pour une source, si déjà collectée."""
    return session.get(SourceMeta, source)


def upsert_source_meta(session: Session, source: str, etag: str | None, last_modified: str | None) -> None:
    """Met à jour les métadonnées HTTP d'une source après un téléchargement réussi."""
    stmt = insert(SourceMeta).values(source=source, etag=etag, last_modified=last_modified)
    stmt = stmt.on_conflict_do_update(
        index_elements=["source"],
        set_={"etag": stmt.excluded.etag, "last_modified": stmt.excluded.last_modified},
    )
    session.execute(stmt)
