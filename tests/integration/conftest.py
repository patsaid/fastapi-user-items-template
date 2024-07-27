"""
This module contains fixtures for integration tests.
"""

import os
from time import sleep

import docker
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.database import get_db
from app.main import app
from app.routes.auth.tokens import create_access_token
from app.routes.auth.utils import hash_pass
from app.routes.users.models import Users
from tests.factories.models_factory import get_random_user_dict
from tests.utils.database_utils import migrate_to_db
from tests.utils.docker_utils import start_database_container


@pytest.fixture(scope="function")
def db_session_integration():
    """
    Provides a database session for integration tests.

    This function starts a database container, creates a database engine,
    applies migrations, and yields a database session for use in integration tests.
    After the tests are completed, it stops the container, removes it, and disposes
    of the engine.

    Returns:
        sqlalchemy.orm.Session: A database session for integration tests.
    """
    container = start_database_container()

    engine = create_engine(os.getenv("TEST_DATABASE_URL"))

    with engine.begin() as connection:
        migrate_to_db("migrations", "alembic.ini", connection)

    session_local = sessionmaker(autocommit=False, autoflush=True, bind=engine)

    db = session_local()

    try:
        yield db
    finally:
        db.close()

    container.stop()
    container.remove()
    engine.dispose()


@pytest.fixture()
def override_get_db_session(db_session_integration):
    """
    Fixture that overrides the `get_db` dependency in the FastAPI app with
        the `db_session_integration` fixture.

    Args:
        db_session_integration (sqlalchemy.orm.Session): The database session.

    Returns:
        None
    """

    def override():
        return db_session_integration

    app.dependency_overrides[get_db] = override


@pytest.fixture(scope="function")
def client(override_get_db_session):
    """
    Fixture that provides a TestClient instance for making HTTP requests to the FastAPI app.

    Args:
        override_get_db_session: The `override_get_db_session` fixture.

    Yields:
        TestClient: The TestClient instance.
    """
    with TestClient(app) as _client:
        yield _client


@pytest.fixture(scope="function")
def admin_user(db_session_integration):
    """
    Fixture that creates an admin user in the database for testing purposes.

    Args:
        db_session (sqlalchemy.orm.Session): The database session.

    Returns:
        app.routes.users.models.Users: The admin user object.
    """
    user_data = get_random_user_dict()
    user_data.pop("id")
    hashed_password = hash_pass(user_data["password"])
    user_data["password"] = hashed_password
    user_data["is_active"] = True
    user_data["role"] = "admin"
    user = Users(**user_data)
    db_session_integration.add(user)
    db_session_integration.commit()
    return user


@pytest.fixture(scope="function")
def access_token(admin_user):
    """
    Fixture that creates an access token for the admin user.

    Args:
        admin_user (app.routes.users.models.Users): The admin user object.

    Returns:
        str: The access token.
    """
    return create_access_token(data={"id": admin_user.id})


@pytest.fixture(scope="function")
def auth_header(access_token):
    """
    Fixture that creates an authorization header with the access token.

    Args:
        access_token (str): The access token.

    Returns:
        dict: The authorization header.
    """
    return {"Authorization": f"Bearer {access_token}"}
