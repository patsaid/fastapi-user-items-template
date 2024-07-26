"""
This module contains integration tests for the items routes.

The integration tests in this module ensure that the items routes of the application
    are functioning correctly. These tests interact with the actual routes and make requests to
    create, read, update, and delete items. The tests verify the expected behavior of the routes
    and check if the responses are as expected.

The following tests are included in this module:
- test_integrate_create_item_successful: Tests the successful creation of an item.
- test_integrate_read_item_successful: Tests the successful retrieval of an item.
- test_integrate_update_item_successful: Tests the successful update of an item.
- test_integrate_delete_item_successful: Tests the successful deletion of an item.
- test_integrate_read_all_items_successful: Tests the successful retrieval of all items.

Note: These tests require a running instance of the application and a connected database to execute
    successfully.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm.session import Session

from app.routes.auth.tokens import create_access_token
from app.routes.auth.utils import hash_pass
from app.routes.category.models import Categories
from app.routes.items.models import Items
from app.routes.users.models import Users
from tests.factories.models_factory import get_random_user_dict


@pytest.fixture
def active_user(db_session_integration: Session):
    """
    Creates and returns an active user.

    Args:
        db_session_integration (Session): The database session.

    Returns:
        Users: The created active user.
    """
    user_data = get_random_user_dict()
    user_data.pop("id")
    hashed_password = hash_pass(user_data["password"])
    user_data["password"] = hashed_password
    user_data["is_active"] = True
    user = Users(**user_data)
    db_session_integration.add(user)
    db_session_integration.commit()
    return user


@pytest.fixture
def access_token(active_user: Users):
    """
    Generate an access token for the given active user.

    Parameters:
    - active_user: An instance of the Users class representing the active user.

    Returns:
    - str: The generated access token.

    """
    return create_access_token(data={"id": active_user.id})


@pytest.fixture
def auth_header(access_token: str):
    """
    Generates an authorization header with the provided access token.

    Parameters:
    - access_token (str): The access token to be included in the header.

    Returns:
    - dict: The authorization header as a dictionary with the access token.

    Example:
    >>> auth_header("my_access_token")
    {'Authorization': 'Bearer my_access_token'}
    """
    return {"Authorization": f"Bearer {access_token}"}


def test_integrate_create_item_successful(
    client: TestClient, db_session_integration: Session, auth_header: dict[str, str]
):
    """
    Test case to verify the successful creation of an item.

    Args:
        client (TestClient): The FastAPI test client.
        db_session_integration (Session): The database session for integration testing.
        auth_header (dict[str, str]): The authentication header for the request.

    Returns:
        None
    """
    # Arrange: Create a category
    category = Categories(name="Test Category")
    db_session_integration.add(category)
    db_session_integration.commit()

    # Prepare payload
    payload = {"name": "Test Item", "category_ids": [category.id]}

    # Act: Make a POST request to create item
    response = client.post("/items/", json=payload, headers=auth_header)

    # Assert: Verify response
    assert response.status_code == 201
    response_data = response.json()
    assert response_data["name"] == payload["name"]
    assert response_data["categories"][0]["id"] == category.id


def test_integrate_read_item_successful(
    client: TestClient,
    db_session_integration: Session,
    auth_header: dict[str, str],
    active_user: Users,
):
    """
    Test case to verify successful retrieval of an item.

    Args:
        client (TestClient): The FastAPI test client.
        db_session_integration (Session): The integration test database session.
        auth_header (dict[str, str]): The authentication header.
        active_user (Users): The active user.

    Returns:
        None
    """
    # Arrange: Create an item
    item = Items(name="Test Item", user_id=active_user.id)
    db_session_integration.add(item)
    db_session_integration.commit()

    # Act: Make a GET request to read the item
    response = client.get(f"/items/{item.id}", headers=auth_header)

    # Assert: Verify response
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["id"] == item.id
    assert response_data["name"] == item.name


def test_integrate_update_item_successful(
    client: TestClient,
    db_session_integration: Session,
    auth_header: dict[str, str],
    active_user: Users,
):
    """
    Test case for successful update of an item.

    Args:
        client (TestClient): The FastAPI test client.
        db_session_integration (Session): The integration test database session.
        auth_header (dict[str, str]): The authentication header for the active user.
        active_user (Users): The active user object.

    Returns:
        None
    """

    # Arrange: Create an item and category
    item = Items(name="Old Item", user_id=active_user.id)
    category = Categories(name="New Category")
    db_session_integration.add_all([item, category])
    db_session_integration.commit()

    # Prepare payload
    payload = {"name": "Updated Item", "category_ids": [category.id]}

    # Act: Make a PUT request to update the item
    response = client.put(f"/items/{item.id}", json=payload, headers=auth_header)

    # Assert: Verify response
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["name"] == payload["name"]
    assert response_data["categories"][0]["id"] == category.id


def test_integrate_delete_item_successful(
    client: TestClient,
    db_session_integration: Session,
    auth_header: dict[str, str],
    active_user: Users,
):
    """
    Test case to verify successful deletion of an item.

    Args:
        client (TestClient): The FastAPI test client.
        db_session_integration (Session): The database session for integration testing.
        auth_header (dict[str, str]): The authentication header for the active user.
        active_user (Users): The active user object.

    Returns:
        None
    """

    # Arrange: Create an item
    item = Items(name="Test Item", user_id=active_user.id)
    db_session_integration.add(item)
    db_session_integration.commit()

    # Act: Make a DELETE request to delete the item
    response = client.delete(f"/items/{item.id}", headers=auth_header)

    # Assert: Verify response
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["id"] == item.id


def test_integrate_read_all_items_successful(
    client: TestClient,
    db_session_integration: Session,
    auth_header: dict[str, str],
    active_user: Users,
):
    """
    Test case to verify the successful retrieval of all items.

    Args:
        client (TestClient): The FastAPI test client.
        db_session_integration (Session): The integration test database session.
        auth_header (dict[str, str]): The authentication header.
        active_user (Users): The active user.

    Returns:
        None
    """
    # Arrange: Create multiple items
    items = [
        Items(name="Item 1", user_id=str(active_user.id)),
        Items(name="Item 2", user_id=str(active_user.id)),
    ]
    db_session_integration.add_all(items)
    db_session_integration.commit()

    # Act: Make a GET request to read all items
    response = client.get("/items/", headers=auth_header)

    # Assert: Verify response
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data) == len(items)
    assert response_data[0]["name"] == items[0].name
    assert response_data[1]["name"] == items[1].name
