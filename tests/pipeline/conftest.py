"""Fixtures pytest pour les tests du pipeline nécessitant une base réelle.

Les tests tournent contre une base PostgreSQL dédiée (`<database>_test`),
jamais contre la base de développement qui contient les vraies données
collectées : compter des lignes y serait faussé par ce contenu réel.
Chaque test s'exécute ensuite dans une transaction annulée en fin de test.
"""

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from backend.app.core.config import get_settings
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
    """Recrée le schéma à neuf à chaque session de tests : la base de test est
    jetable, et ceci évite un schéma figé qui divergerait des modèles après
    une migration Alembic (colonne ajoutée, etc.)."""
    engine = create_engine(_url_base_test())
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def db_session(engine):
    """Session isolée par savepoint : un `session.commit()` dans le code testé
    (ex. génération d'analyses IA par lot) ne valide qu'un SAVEPOINT imbriqué,
    jamais la transaction externe — celle-ci est toujours annulée en fin de
    test, quel que soit le nombre de commits internes effectués."""
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection, join_transaction_mode="create_savepoint")

    yield session

    session.close()
    transaction.rollback()
    connection.close()
