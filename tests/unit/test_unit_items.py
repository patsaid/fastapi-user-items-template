"""
This file contains the unit tests for the items routes.
"""

from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.routes.items.models import Items
from tests.factories.models_factory import get_random_item_dict


def mock_output(return_value=None):
    """
    A helper function that creates a mock function with a specified return value.

    Parameters:
    - return_value: The value that the mock function should return.

    Returns:
    - A mock function that always returns the specified return value.
    """
    return lambda *args, **kwargs: return_value


def test_unit_create_item_successfully(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    mock_admin_user: dict[str, Any],
    mock_db_operations: None,
):
    """
    Test case to verify the successful creation of an item.

    Args:
        client (TestClient): The FastAPI test client.
        monkeypatch (pytest.MonkeyPatch): The pytest monkeypatch fixture.
        mock_admin_user (dict[str, Any]): The mock admin user dictionary.
        mock_db_operations (None): The mock database operations.

    Returns:
        None
    """
    item_dict = get_random_item_dict()
    item_dict["user_id"] = mock_admin_user["id"]
    item_dict.pop("categories")
    item_instance = Items(**item_dict)

    monkeypatch.setattr("sqlalchemy.orm.Query.first", mock_output(item_instance))

    payload = item_dict.copy()
    payload.pop("id")
    response = client.post("/items", json=payload)

    response_payload = response.json()
    response_payload.pop("categories")
    expected_payload = item_dict.copy()
    expected_payload["id"] = 1

    assert response.status_code == 201
    assert response_payload == expected_payload


def test_unit_create_item_internal_error(
    client: TestClient, monkeypatch: pytest.MonkeyPatch, mock_admin_user: dict[str, Any]
):
    """
    Test case to verify the behavior of creating an item when an internal server error occurs.

    Args:
        client (TestClient): The FastAPI test client.
        monkeypatch (pytest.MonkeyPatch): The pytest monkeypatch fixture.
        mock_admin_user (dict[str, Any]): The mock admin user dictionary.
        mock_db_operations_exception (None): The mock database operations exception.

    Returns:
        None
    """
    item_dict = get_random_item_dict()
    item_dict["user_id"] = mock_admin_user["id"]
    item_dict.pop("categories")
    item_instance = Items(**item_dict)

    monkeypatch.setattr("sqlalchemy.orm.Query.first", mock_output(item_instance))

    payload = item_dict.copy()
    payload.pop("id")

    response = client.post("/items", json=payload)
    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error"}


def test_unit_update_item_successfully(
    client: TestClient,
    mock_admin_user: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
    mock_db_operations: None,
):
    """
    Test case to verify the successful update of an item.

    Args:
        client (TestClient): The FastAPI test client.
        mock_admin_user (dict[str, Any]): The mock admin user data.
        monkeypatch (pytest.MonkeyPatch): The monkeypatch fixture.
        mock_db_operations (None): The mock database operations.

    Returns:
        None
    """
    item_dict = get_random_item_dict()
    item_dict["user_id"] = mock_admin_user["id"]
    item_dict.pop("categories")
    item_instance = Items(**item_dict)

    monkeypatch.setattr("sqlalchemy.orm.Query.first", mock_output(item_instance))

    body = item_dict.copy()
    response = client.put(f"/items/{item_dict['id']}", json=body)
    response_payload = response.json()
    response_payload.pop("categories")

    assert response.status_code == 200
    assert response_payload == item_dict


def test_unit_update_item_not_found(
    client: TestClient, mock_admin_user: dict[str, Any], monkeypatch: pytest.MonkeyPatch
):
    """
    Test case to verify that updating an item that does not exist returns a
    404 status code and the appropriate error message.

    Args:
        client (TestClient): The FastAPI test client.
        mock_admin_user (dict[str, Any]): A dictionary representing a mock admin user.
        monkeypatch (pytest.MonkeyPatch): The pytest monkeypatch fixture.

    Returns:
        None
    """
    item_dict = get_random_item_dict()
    item_dict["user_id"] = mock_admin_user["id"]
    item_dict.pop("categories")

    monkeypatch.setattr("sqlalchemy.orm.Query.first", mock_output())

    body = item_dict.copy()
    body.pop("id")
    response = client.put(f"/items/{item_dict['id']}", json=body)
    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found"}


def test_unit_update_item_internal_error(
    client: TestClient, mock_admin_user: dict[str, Any], monkeypatch: pytest.MonkeyPatch
):
    """
    Test case to verify the behavior of updating an item when an internal server error occurs.

    Args:
        client (TestClient): The FastAPI test client.
        mock_admin_user (dict[str, Any]): A dictionary representing the mock admin user.
        monkeypatch (pytest.MonkeyPatch): The pytest monkeypatch fixture.

    Raises:
        Exception: If an internal server error occurs during the update.

    Returns:
        None
    """
    item_dict = get_random_item_dict()
    item_dict["user_id"] = mock_admin_user["id"]
    item_dict.pop("categories")
    item_instance = Items(**item_dict)

    def mock_update_item_exception(*args, **kwargs):
        raise Exception("Internal server error")

    monkeypatch.setattr("sqlalchemy.orm.Query.first", mock_output(item_instance))
    monkeypatch.setattr("sqlalchemy.orm.Session.commit", mock_update_item_exception)

    body = item_dict.copy()
    body.pop("id")
    response = client.put(f"/items/{item_dict['id']}", json=body)
    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error"}


@pytest.mark.parametrize("item", [get_random_item_dict() for _ in range(3)])
def test_unit_get_single_item_successfully(
    client: TestClient, monkeypatch: pytest.MonkeyPatch, item: Any
):
    """
    Test case to verify that a single item can be retrieved successfully.

    Args:
        client (TestClient): The FastAPI test client.
        monkeypatch (pytest.MonkeyPatch): The pytest monkeypatch fixture.
        item (Any): The item to be retrieved.

    Returns:
        None
    """
    item.pop("categories")

    monkeypatch.setattr("sqlalchemy.orm.Query.first", mock_output(Items(**item)))
    response = client.get(f"/items/{item['id']}")
    response_payload = response.json()
    response_payload.pop("categories")

    assert response.status_code == 200
    assert response_payload == item


@pytest.mark.parametrize("item", [get_random_item_dict() for _ in range(3)])
def test_unit_get_single_item_not_found(
    client: TestClient, monkeypatch: pytest.MonkeyPatch, item: Any
):
    """
    Test case to verify that a single item is not found.

    Args:
        client (TestClient): The FastAPI test client.
        monkeypatch (pytest.MonkeyPatch): The pytest monkeypatch fixture.
        item (Any): The item to be tested.

    Returns:
        None
    """
    monkeypatch.setattr("sqlalchemy.orm.Query.first", mock_output())
    response = client.get(f"/items/{item['id']}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found"}


def test_unit_delete_item_successfully(
    client: TestClient, mock_admin_user: dict[str, Any], monkeypatch: pytest.MonkeyPatch
):
    """
    Test case to verify successful deletion of an item.

    Args:
        client (TestClient): The FastAPI TestClient instance.
        mock_admin_user (dict[str, Any]): A dictionary representing the mock admin user.
        monkeypatch (pytest.MonkeyPatch): The pytest MonkeyPatch instance.

    Returns:
        None
    """
    item_dict = get_random_item_dict()
    item_dict["user_id"] = mock_admin_user["id"]
    item_dict.pop("categories")
    item_instance = Items(**item_dict)

    monkeypatch.setattr("sqlalchemy.orm.Query.first", mock_output(item_instance))
    monkeypatch.setattr("sqlalchemy.orm.Session.delete", mock_output())
    monkeypatch.setattr("sqlalchemy.orm.Session.commit", mock_output())

    response = client.delete(f"/items/{item_dict['id']}")

    assert response.status_code == 200
    assert response.json() == {"id": item_dict["id"]}


def test_unit_delete_item_not_found(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
):
    """
    Test case to verify the behavior when trying to delete an item that is not found.

    Args:
        client (TestClient): The FastAPI TestClient instance.
        mock_admin_user (dict[str, Any]): A dictionary representing the mock admin user.
        monkeypatch (pytest.MonkeyPatch): The pytest MonkeyPatch fixture.

    Returns:
        None
    """
    monkeypatch.setattr("sqlalchemy.orm.Query.first", mock_output())
    monkeypatch.setattr("sqlalchemy.orm.Session.commit", mock_output())

    response = client.delete("/items/1")
    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found"}


def test_unit_delete_item_internal_error(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
):
    """
    Test case to verify the behavior of deleting an item when an internal server error occurs.

    Args:
        client (TestClient): The FastAPI test client.
        mock_admin_user (dict[str, Any]): A dictionary representing the mock admin user.
        monkeypatch (pytest.MonkeyPatch): The pytest monkeypatch fixture.

    Raises:
        Exception: If an internal server error occurs during the deletion process.

    Returns:
        None
    """
    item_dict = get_random_item_dict()
    item_dict.pop("categories")
    item_instance = Items(**item_dict)

    def mock_delete_item_exception(*args, **kwargs):
        raise Exception("Internal server error")

    monkeypatch.setattr("sqlalchemy.orm.Query.first", mock_output(item_instance))
    monkeypatch.setattr("sqlalchemy.orm.Session.delete", mock_output())
    monkeypatch.setattr("sqlalchemy.orm.Session.commit", mock_delete_item_exception)

    response = client.delete(f"/items/{item_dict['id']}")
    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error"}
