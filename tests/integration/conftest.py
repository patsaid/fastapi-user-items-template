import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.routes.auth.tokens import create_access_token
from app.routes.auth.utils import hash_pass
from app.db.database import get_db
from app.main import app
from app.routes.users.models import Users
from tests.factories.models_factory import get_random_user_dict
from tests.utils.database_utils import migrate_to_db
from tests.utils.docker_utils import start_database_container


@pytest.fixture(scope="function")
def db_session_integration():
    container = start_database_container()

    engine = create_engine(os.getenv("TEST_DATABASE_URL"))

    with engine.begin() as connection:
        migrate_to_db("migrations", "alembic.ini", connection)

    SessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=engine)

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close

    container.stop()
    container.remove()
    engine.dispose()


@pytest.fixture()
def override_get_db_session(db_session_integration):
    def override():
        return db_session_integration

    app.dependency_overrides[get_db] = override


@pytest.fixture(scope="function")
def client(override_get_db_session):
    with TestClient(app) as _client:
        yield _client


@pytest.fixture(scope="function")
def admin_user(db_session_integration):
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
    return create_access_token(data={"id": admin_user.id})

@pytest.fixture(scope="function")
def auth_header(access_token):
    return {"Authorization": f"Bearer {access_token}"}
