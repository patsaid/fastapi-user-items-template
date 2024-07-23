from app.main import app
from app.routes.auth.utils import hash_pass
from app.routes.auth.tokens import get_current_user
from app.routes.users.models import Users
import uuid


from pydantic import BaseModel

from tests.factories.models_factory import get_random_user_dict


class LoginRequestTest(BaseModel):
    username: str
    password: str


def mock_output(return_value=None):
    return lambda *args, **kwargs: return_value


"""
- [ ] Test POST /users/signin success
"""


def test_unit_post_signin_success(client, monkeypatch):
    user_dict = get_random_user_dict()
    user_instance = Users(**user_dict)
    user_instance.password = hash_pass(user_instance.password)
    
    # Mock the query method to return the user
    monkeypatch.setattr("sqlalchemy.orm.Query.first", mock_output(user_instance))

    # Create a payload that matches the mock user details
    login_payload = {
        "email": user_dict["email"],
        "password": user_dict["password"],
    }


    response = client.post("/users/signin", json=login_payload)

    # Print response for debugging
    print(f"Response status code: {response.status_code}")
    print(f"Response body: {response.json()}")

    # Check for successful login
    assert response.status_code == 200


"""
- [ ] Test POST /users/signin with invalid credentials
"""


def test_unit_post_signin_invalid_credentials(client, monkeypatch):
    user_dict = get_random_user_dict()
    user_instance = Users(**user_dict)
    user_instance.password = hash_pass(user_instance.password)
    
    # Mock the query method to return the user
    monkeypatch.setattr("sqlalchemy.orm.Query.first", mock_output(user_instance))

    login_payload = {"email": user_dict["email"], "password": "wrong-password"}
    response = client.post("/users/signin", json=login_payload)

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid credentials."}


"""
- [ ] Test POST /users/signup success
"""


def test_unit_post_signup_success(client):
    user_dict = get_random_user_dict()

    signup_payload = {
        "email": user_dict["email"],
        "password": user_dict["password"],
        "name": user_dict["name"],
    }
    response = client.post("/users/signup", json=signup_payload)

    assert response.status_code == 201
    assert response.json() == {"detail": "User created successfully."}


"""
- [ ] Test POST /users/signup when user already exists
"""


def test_unit_post_signup_user_exists(client, monkeypatch):
    user_dict = get_random_user_dict()
    user_instance = Users(**user_dict)
    
    # Mock the query method to return the user
    monkeypatch.setattr("sqlalchemy.orm.Query.first", mock_output(user_instance))

    signup_payload = {
        "email": user_dict["email"],
        "password": user_dict["password"],
        "name": user_dict["name"],
    }
    response = client.post("/users/signup", json=signup_payload)

    assert response.status_code == 409
    assert response.json() == {"detail": "User with this email already exists."}


"""
- [ ] Test GET /users/me success
"""


def test_unit_get_me_success(client, mock_admin_user):
    response = client.get("/users/me")

    response_payload = response.json()
    response_payload.pop("items")

    assert response.status_code == 200
    assert response_payload == {
        "id": mock_admin_user["id"],
        "email": mock_admin_user["email"],
        "name": mock_admin_user["name"],
        "role": mock_admin_user["role"],
        "is_active": mock_admin_user["is_active"],
    }


"""
- [ ] Test GET /users/me unauthorized
"""


def test_unit_get_me_unauthorized(client):
    # Create an admin user and override the dependency
    user_admin_dict = get_random_user_dict()
    # Set the user id to None to simulate an unauthorized user
    user_admin_dict["id"] = None
    
    # Override dependency in FastAPI app
    def mock_get_current_user():
        return Users(**user_admin_dict)
    
    app.dependency_overrides[get_current_user] = mock_get_current_user
    response = client.get("/users/me")

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid credentials."}



"""
- [ ] Test GET /users/ success with valid admin user
"""
from unittest.mock import MagicMock
def mock_query_users(*args, **kwargs):
    class MockQuery:
        def __init__(self, users):
            self.users = users
        
        def offset(self, skip):
            self.skip = skip
            return self
        
        def limit(self, limit):
            self.limit = limit
            return self
        
        def all(self):
            return self.users[self.skip:self.skip+self.limit]

    mock_users = [
        Users(id=str(uuid.uuid4()), name="User 1", email="user1@example.com", role="user"),
        Users(id=str(uuid.uuid4()), name="User 2", email="user2@example.com", role="user"),
    ]

    return MockQuery(mock_users)


def test_unit_get_users_success(client, monkeypatch):
    # Create an admin user and override the dependency
    user_admin_dict = get_random_user_dict()
    user_admin_dict["role"] = "admin"
    user_admin_dict["is_active"] = True
    
    # Override dependency in FastAPI app
    def mock_get_current_user():
        return Users(**user_admin_dict)
    app.dependency_overrides[get_current_user] = mock_get_current_user
    
    # Mock the query method to return a list of users
    mock_query_instance = mock_query_users()
    mock_db_session = MagicMock()
    mock_db_session.query.return_value = mock_query_instance

    monkeypatch.setattr("app.db.database.get_db", lambda: mock_db_session)
    
    response = client.get("/users/", params={"skip": 0, "limit": 5})
    response_payload = response.json()

    assert response.status_code == 200
    assert isinstance(response_payload, list)
    assert len(response_payload) > 0

"""
- [ ] Test GET /users/ forbidden access without admin rights
"""
def test_unit_get_users_unauthorized(client, monkeypatch):
    # Create an admin user and override the dependency
    user_admin_dict = get_random_user_dict()
    user_admin_dict["role"] = "user"
    user_admin_dict["is_active"] = True
    
    # Override dependency in FastAPI app
    def mock_get_current_user():
        return Users(**user_admin_dict)
    app.dependency_overrides[get_current_user] = mock_get_current_user
    
    # Mock the query method to return a list of users
    mock_query_instance = mock_query_users()
    mock_db_session = MagicMock()
    mock_db_session.query.return_value = mock_query_instance

    monkeypatch.setattr("app.db.database.get_db", lambda: mock_db_session)
    
    response = client.get("/users/", params={"skip": 0, "limit": 5})
    response_payload = response.json()
    
    assert response.status_code == 403
    assert response.json() == {"detail": "Insufficient permissions"}
