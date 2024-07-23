import pytest
from app.routes.auth.tokens import get_current_user
from app.routes.users.models import Users
from tests.factories.models_factory import get_random_user_dict
from app.main import app

@pytest.fixture(scope="function")
def mock_admin_user(monkeypatch):
    user_dict = get_random_user_dict()
    user_dict["role"] = "admin"
    user_dict["is_active"] = True
    
    def mock_get_current_user():
        return Users(**user_dict)
    app.dependency_overrides[get_current_user] = mock_get_current_user

    return user_dict

@pytest.fixture(scope="function")
def mock_current_user(monkeypatch):
    user_dict = get_random_user_dict()
    user_dict["role"] = "admin"
    user_dict["is_active"] = True

    def mock_get_current_user():
        return Users(**user_dict)
    
    app.dependency_overrides[get_current_user] = mock_get_current_user
    return user_dict

@pytest.fixture(scope="function")
def mock_db_operations(monkeypatch):
    def mock_add(self, instance):
        instance.id = 1
        return instance

    def mock_commit(self):
        return None

    def mock_refresh(self, instance):
        return None

    monkeypatch.setattr("sqlalchemy.orm.Session.add", mock_add)
    monkeypatch.setattr("sqlalchemy.orm.Session.commit", mock_commit)
    monkeypatch.setattr("sqlalchemy.orm.Session.refresh", mock_refresh)
    return None


@pytest.fixture(scope="function")
def mock_db_operations_exception(monkeypatch):
    def mock_add(self, instance):
        instance.id = 1
        return instance

    def mock_create_item_exception(*args, **kwargs):
        raise Exception("Internal server error")

    def mock_refresh(self, instance):
        return None

    monkeypatch.setattr("sqlalchemy.orm.Session.add", mock_add)
    monkeypatch.setattr("sqlalchemy.orm.Session.commit", mock_create_item_exception)
    monkeypatch.setattr("sqlalchemy.orm.Session.refresh", mock_refresh)
    return None
