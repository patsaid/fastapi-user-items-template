"""
This module contains fixtures used for testing the FastAPI application.

Fixtures are functions that provide a fixed baseline for tests. They are used to
initialize and set up the environment for tests, such as creating a test database,
starting a test client, etc.
"""

import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from tests.utils.database_utils import migrate_to_db
from tests.utils.docker_utils import start_database_container


@pytest.fixture(scope="session")
def db_session():
    """
    Fixture that provides a database session for testing.

    This fixture starts a database container, creates a test database, and sets up a
    SQLAlchemy session for testing. The session is available throughout the entire test
    session and is disposed of after all tests have finished.

    Returns:
        sqlalchemy.orm.session.Session: The database session.
    """
    container = start_database_container()

    engine = create_engine(os.getenv("TEST_DATABASE_URL"))
    with engine.begin() as connection:
        migrate_to_db("migrations", "alembic.ini", connection)

    session_local = sessionmaker(autocommit=False, autoflush=True, bind=engine)
    yield session_local

    container.stop()
    container.remove()
    engine.dispose()


@pytest.fixture(scope="function")
def client():
    """
    Fixture that provides a test client for the FastAPI application.

    This fixture creates a test client using the FastAPI `TestClient` class. The client
    is available within the scope of each test function.

    Returns:
        fastapi.testclient.TestClient: The test client.
    """
    with TestClient(app) as _client:
        yield _client
