"""Fixtures pytest pour les tests de l'API : base PostgreSQL et Redis dédiés aux tests.

Comme pour `tests/pipeline/`, on ne teste jamais contre la base ou le cache
de développement qui contiennent les vraies données collectées.
"""

import pytest
import redis
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

import backend.app.core.cache as cache_module
from backend.app.core.config import get_settings
from backend.app.core.db import get_db
from backend.app.main import app
from backend.app.models import Base


def _url_base_test() -> str:
    return get_settings().database_url + "_test"


@pytest.fixture(scope="session", autouse=True)
def _creer_base_test():
    settings = get_settings()
    nom_base = settings.database_url.rsplit("/", 1)[-1] + "_test"
    engine_admin = create_engine(settings.database_url.rsplit("/", 1)[0] + "/postgres")
    with engine_admin.connect() as connexion:
        connexion = connexion.execution_options(isolation_level="AUTOCOMMIT")
        existe = connexion.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :nom"), {"nom": nom_base}
        ).first()
        if existe is None:
            connexion.execute(text(f'CREATE DATABASE "{nom_base}"'))
    engine_admin.dispose()


@pytest.fixture(scope="session")
def engine(_creer_base_test):
    engine = create_engine(_url_base_test())
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def db_session(engine):
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(autouse=True)
def _redis_test(monkeypatch):
    """Base Redis dédiée aux tests API (index 2), distincte du pipeline (1) et du dev (0)."""
    url_test = get_settings().redis_url.rsplit("/", 1)[0] + "/2"
    client = redis.from_url(url_test, decode_responses=True)
    client.flushdb()
    monkeypatch.setattr(cache_module, "_client", client)
    yield
    client.flushdb()


@pytest.fixture
def client(db_session):
    def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
