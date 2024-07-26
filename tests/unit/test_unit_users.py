"""
This module contains unit tests for the users module.
"""

import uuid
from typing import Any
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from pytest import MonkeyPatch

from app.main import app
from app.routes.auth.tokens import get_current_user
from app.routes.users.models import Users
from tests.factories.models_factory import get_random_user_dict


def mock_admin_user() -> dict[str, Any]:
    """
    Returns a dictionary representing a mock admin user.

    Returns:
        dict[str, Any]: A dictionary containing the following keys:
            - "id": A string representing the unique identifier of the user.
            - "email": A string representing the email address of the user.
            - "name": A string representing the name of the user.
            - "role": A string representing the role of the user.
            - "is_active": A boolean indicating whether the user is active or not.
    """
    return {
        "id": str(uuid.uuid4()),
        "email": "admin@example.com",
        "name": "Admin User",
        "role": "admin",
        "is_active": True,
    }


def test_unit_get_me_success(client: TestClient, mock_current_user: dict[str, Any]):
    """
    Test case for successful retrieval of user information.

    Args:
        client (TestClient): The FastAPI test client.

    Returns:
        None
    """
    response = client.get("/users/me")

    response_payload = response.json()
    response_payload.pop("items")

    assert response.status_code == 200
    assert response_payload == {
        "id": mock_current_user["id"],
        "email": mock_current_user["email"],
        "name": mock_current_user["name"],
        "role": mock_current_user["role"],
        "is_active": mock_current_user["is_active"],
    }


def test_unit_get_me_unauthorized(client: TestClient):
    """
    Test case to verify that an unauthorized user cannot access the '/users/me' endpoint.
    """

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


def mock_query_users(*args, **kwargs):
    """
    Mocks the query_users function by returning a mock query object.

    Args:
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.

    Returns:
        MockQuery: A mock query object that simulates the behavior of the query object.

    """

    class MockQuery:
        """
        A mock implementation of the query object for testing purposes.

        This class provides methods to simulate the behavior of a query object
        in a database. It allows setting the offset, limit, and retrieving a
        subset of users from a given list.

        Attributes:
            users (list): The list of users to query.
            skip (int): The offset value for the query.
            query_limit (int): The limit value for the query.
        """

        def __init__(self, users):
            self.users = users

        def offset(self, skip):
            """
            Sets the offset for the query.

            Args:
                skip (int): The number of items to skip.

            Returns:
                self: The current instance of the class.
            """
            self.skip = skip
            return self

        def limit(self, limit):
            """
            Sets the limit for the query.

            Args:
                limit (int): The maximum number of items to retrieve.

            Returns:
                self: The current instance of the query builder.

            """
            self.query_limit = limit
            return self

        def all(self):
            """
            Returns a subset of users based on the skip and query_limit attributes.
            """
            return self.users[self.skip : self.skip + self.query_limit]

    mock_users = [
        Users(
            id=str(uuid.uuid4()), name="User 1", email="user1@example.com", role="user"
        ),
        Users(
            id=str(uuid.uuid4()), name="User 2", email="user2@example.com", role="user"
        ),
    ]

    return MockQuery(mock_users)


@pytest.mark.skip(reason="Skipping this test class for now")
def test_unit_get_users_success(client: TestClient, monkeypatch: MonkeyPatch):
    """
    Test case for successful retrieval of users.

    Args:
        client (TestClient): The FastAPI test client.
        monkeypatch (MonkeyPatch): The pytest monkeypatch fixture.

    Returns:
        None
    """
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


def test_unit_get_users_unauthorized(client: TestClient, monkeypatch: MonkeyPatch):
    """
    Test case to verify that a user with insufficient permissions receives a 403 Forbidden response
    when trying to access the list of users.

    Args:
        client (TestClient): The FastAPI test client.
        monkeypatch (MonkeyPatch): The pytest monkeypatch fixture.

    Returns:
        None
    """
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

    assert response.status_code == 403
    assert response.json() == {"detail": "Insufficient permissions"}
