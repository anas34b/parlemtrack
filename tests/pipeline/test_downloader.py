"""Tests du downloader : détection de changement via ETag/Last-Modified, réseau mocké."""

import io
import zipfile
from unittest.mock import Mock, patch

from pipeline.collect.downloader import a_change, telecharger_zip
from pipeline.store.collecte import get_source_meta


def _reponse_head(etag: str, last_modified: str) -> Mock:
    reponse = Mock()
    reponse.headers = {"ETag": etag, "Last-Modified": last_modified}
    reponse.raise_for_status = Mock()
    return reponse


def _zip_vide_bytes() -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("test.json", "{}")
    return buffer.getvalue()


def test_a_change_vrai_si_source_jamais_collectee(db_session) -> None:
    with patch("pipeline.collect.downloader.requests.head", return_value=_reponse_head("etag-1", "date-1")):
        assert a_change(db_session, "scrutins", "https://example.org/x.zip") is True


def test_a_change_faux_si_etag_identique(db_session) -> None:
    from pipeline.store.collecte import upsert_source_meta

    upsert_source_meta(db_session, "scrutins", "etag-1", "date-1")
    db_session.flush()

    with patch("pipeline.collect.downloader.requests.head", return_value=_reponse_head("etag-1", "date-1")):
        assert a_change(db_session, "scrutins", "https://example.org/x.zip") is False


def test_a_change_vrai_si_etag_different(db_session) -> None:
    from pipeline.store.collecte import upsert_source_meta

    upsert_source_meta(db_session, "scrutins", "etag-1", "date-1")
    db_session.flush()

    with patch("pipeline.collect.downloader.requests.head", return_value=_reponse_head("etag-2", "date-2")):
        assert a_change(db_session, "scrutins", "https://example.org/x.zip") is True


def test_telecharger_zip_saute_si_inchange(db_session) -> None:
    from pipeline.store.collecte import upsert_source_meta

    upsert_source_meta(db_session, "scrutins", "etag-1", "date-1")
    db_session.flush()

    with patch("pipeline.collect.downloader.requests.head", return_value=_reponse_head("etag-1", "date-1")):
        resultat = telecharger_zip(db_session, "scrutins", "https://example.org/x.zip")

    assert resultat is None


def test_telecharger_zip_met_a_jour_les_metadonnees(db_session) -> None:
    reponse_get = Mock()
    reponse_get.headers = {"ETag": "etag-neuf", "Last-Modified": "date-neuve"}
    reponse_get.content = _zip_vide_bytes()
    reponse_get.raise_for_status = Mock()

    with (
        patch("pipeline.collect.downloader.requests.head", return_value=_reponse_head(None, None)),
        patch("pipeline.collect.downloader.requests.get", return_value=reponse_get),
    ):
        archive = telecharger_zip(db_session, "scrutins", "https://example.org/x.zip")
    db_session.flush()

    assert isinstance(archive, zipfile.ZipFile)
    assert "test.json" in archive.namelist()
    meta = get_source_meta(db_session, "scrutins")
    assert meta.etag == "etag-neuf"
