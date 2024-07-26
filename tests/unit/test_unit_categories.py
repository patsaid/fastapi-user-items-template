"""
This module contains unit tests for the category routes in the FastAPI application.

The tests cover the following scenarios:
- Test POST create category successfully
- Test POST create category internal server error
- Test PUT update category successfully
- Test PUT update category not found
- Test PUT update category internal server error
- Test GET single category by id successfully
- Test GET single category by id not found
- Test DELETE category successfully
- Test DELETE category not found
- Test DELETE category internal server error
"""

from typing import Any
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.routes.category.models import Categories
from tests.factories.models_factory import get_random_category_dict


def mock_output(return_value=None):
    """
    A helper function that creates a mock function with a specified return value.

    Parameters:
    - return_value: The value that the mock function should return.

    Returns:
    - A mock function that returns the specified return value.
    """
    return lambda *args, **kwargs: return_value


def test_unit_create_category_successfully(
    client: TestClient,
    mock_admin_user: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
    mock_db_operations: None,
):
    """
    Test case to verify the successful creation of a category.

    Args:
        client (TestClient): The FastAPI test client.
        mock_admin_user (dict[str, Any]): The mock admin user.
        monkeypatch (pytest.MonkeyPatch): The pytest monkeypatch object.
    """
    category_dict = get_random_category_dict()
    category_instance = Categories(**category_dict)

    monkeypatch.setattr(
        "sqlalchemy.orm.Query.first", lambda *args, **kwargs: category_instance
    )

    payload = category_dict.copy()
    payload.pop("id")
    response = client.post("/categories", json=payload)

    response_payload = response.json()
    expected_payload = category_dict.copy()
    expected_payload["id"] = 1  # Ensure ID is correctly assigned

    assert response.status_code == 201
    assert response_payload == expected_payload


def test_unit_create_category_internal_error(
    client: TestClient,
    mock_admin_user: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
):
    """
    Test case to verify the behavior of creating a category when an internal server error occurs.

    Args:
        client (TestClient): The FastAPI TestClient instance.
        monkeypatch (pytest.MonkeyPatch): The pytest MonkeyPatch instance.

    Raises:
        Exception: If an internal server error occurs during category creation.

    Returns:
        None
    """
    category_dict = get_random_category_dict()

    def mock_create_category_exception(*args, **kwargs):
        raise Exception("Internal server error")

    monkeypatch.setattr("sqlalchemy.orm.Session.commit", mock_create_category_exception)

    payload = category_dict.copy()
    payload.pop("id")

    response = client.post("/categories", json=payload)
    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error"}


def test_unit_update_category_successfully(
    client: TestClient, mock_admin_user: dict[str, Any], monkeypatch: pytest.MonkeyPatch
):
    """
    Test case to verify successful update of a category.

    Args:
        client (TestClient): The FastAPI test client.
        mock_admin_user (dict[str, Any]): The mock admin user.
        monkeypatch (pytest.MonkeyPatch): The pytest monkeypatch fixture.

    Returns:
        None
    """
    category_dict = get_random_category_dict()
    category_instance = Categories(**category_dict)

    monkeypatch.setattr("sqlalchemy.orm.Query.first", mock_output(category_instance))
    monkeypatch.setattr("sqlalchemy.orm.Session.commit", mock_output())
    monkeypatch.setattr("sqlalchemy.orm.Session.refresh", mock_output())

    body = category_dict.copy()
    body.pop("id")
    response = client.put(f"/categories/{category_dict['id']}", json=body)
    response_payload = response.json()
    response_payload.pop("id")  # Adjust expected response if id is auto-generated

    assert response.status_code == 200
    assert response.json() == category_dict


def test_unit_update_category_not_found(
    client: TestClient, mock_admin_user: dict[str, Any], monkeypatch: pytest.MonkeyPatch
):
    """
    Test case to verify the behavior when updating a category that is not found.

    Args:
        client (TestClient): The FastAPI test client.
        mock_admin_user (dict[str, Any]): The mock admin user.
        monkeypatch (pytest.MonkeyPatch): The pytest monkeypatch fixture.

    Returns:
        None
    """
    category_dict = get_random_category_dict()

    monkeypatch.setattr("sqlalchemy.orm.Query.first", mock_output())
    monkeypatch.setattr("sqlalchemy.orm.Session.commit", mock_output())
    monkeypatch.setattr("sqlalchemy.orm.Session.refresh", mock_output())

    body = category_dict.copy()
    body.pop("id")
    response = client.put(f"/categories/{category_dict['id']}", json=body)
    assert response.status_code == 404
    assert response.json() == {"detail": "Category not found"}


def test_unit_update_category_internal_error(
    client: TestClient, mock_admin_user: dict[str, Any], monkeypatch: pytest.MonkeyPatch
):
    """
    Test case to verify the behavior when an internal server error occurs during category update.

    Args:
        client (TestClient): The FastAPI test client.
        mock_admin_user (dict[str, Any]): The mock admin user.
        monkeypatch (pytest.MonkeyPatch): The pytest monkeypatch fixture.

    Raises:
        Exception: If an internal server error occurs during the category update.

    Returns:
        None
    """
    category_dict = get_random_category_dict()
    category_instance = Categories(**category_dict)

    def mock_update_category_exception(*args, **kwargs):
        raise Exception("Internal server error")

    monkeypatch.setattr("sqlalchemy.orm.Query.first", mock_output(category_instance))
    monkeypatch.setattr("sqlalchemy.orm.Session.commit", mock_update_category_exception)
    monkeypatch.setattr("sqlalchemy.orm.Session.refresh", mock_output())

    body = category_dict.copy()
    body.pop("id")
    response = client.put(f"/categories/{category_dict['id']}", json=body)
    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error"}


@pytest.mark.parametrize("category", [get_random_category_dict() for _ in range(3)])
def test_unit_get_single_category_successfully(
    client: TestClient, monkeypatch: pytest.MonkeyPatch, category: Any
):
    """
    Test case to verify that a single category can be retrieved successfully.

    Args:
        client (TestClient): The FastAPI test client.
        monkeypatch (pytest.MonkeyPatch): The pytest monkeypatch fixture.
        category (Any): The category data to be used for the test.

    Returns:
        None
    """
    monkeypatch.setattr(
        "sqlalchemy.orm.Query.first", mock_output(Categories(**category))
    )
    response = client.get(f"/categories/{category['id']}")

    assert response.status_code == 200
    assert response.json() == category


@pytest.mark.parametrize("category", [get_random_category_dict() for _ in range(3)])
def test_unit_get_single_category_not_found(
    client: TestClient, monkeypatch: pytest.MonkeyPatch, category: Any
):
    """
    Test case to verify that a 404 response is returned when attempting to get a single category that does not exist.

    Args:
        client (TestClient): The FastAPI test client.
        monkeypatch (pytest.MonkeyPatch): The pytest monkeypatch fixture.
        category (Any): The category object used for testing.
    """
    monkeypatch.setattr("sqlalchemy.orm.Query.first", mock_output())
    response = client.get(f"/categories/{category['id']}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Category not found"}


def test_unit_delete_category_successfully(
    client: TestClient, mock_admin_user: dict[str, Any], monkeypatch: pytest.MonkeyPatch
):
    """
    Test case to verify successful deletion of a category.

    Args:
        client (TestClient): The FastAPI test client.
        mock_admin_user (dict[str, Any]): A dictionary representing a mock admin user.
        monkeypatch (pytest.MonkeyPatch): The pytest monkeypatch fixture.

    Returns:
        None
    """
    category_dict = get_random_category_dict()
    category_instance = Categories(**category_dict)

    monkeypatch.setattr("sqlalchemy.orm.Query.first", mock_output(category_instance))
    monkeypatch.setattr("sqlalchemy.orm.Session.delete", mock_output())
    monkeypatch.setattr("sqlalchemy.orm.Session.commit", mock_output())

    response = client.delete(f"/categories/{category_dict['id']}")

    assert response.status_code == 200
    assert response.json() == {"id": category_dict["id"]}


def test_unit_delete_category_not_found(
    client: TestClient, mock_admin_user: dict[str, Any], monkeypatch: pytest.MonkeyPatch
):
    """
    Test case to verify the behavior when trying to delete a category that does not exist.

    Args:
        client (TestClient): The FastAPI test client.
        mock_admin_user (dict[str, Any]): A dictionary representing the mock admin user.
        monkeypatch (pytest.MonkeyPatch): The pytest monkeypatch fixture.

    Returns:
        None
    """
    monkeypatch.setattr("sqlalchemy.orm.Query.first", mock_output())
    monkeypatch.setattr("sqlalchemy.orm.Session.commit", mock_output())

    response = client.delete("/categories/1")
    assert response.status_code == 404
    assert response.json() == {"detail": "Category not found"}


def test_unit_delete_category_internal_error(
    client: TestClient, mock_admin_user: dict[str, Any], monkeypatch: pytest.MonkeyPatch
):
    """
    Test case to verify the behavior of deleting a category when an internal server error occurs.

    Args:
        client (TestClient): The FastAPI test client.
        mock_admin_user (dict[str, Any]): The mocked admin user.
        monkeypatch (pytest.MonkeyPatch): The pytest monkeypatch fixture.

    Raises:
        Exception: If an internal server error occurs during the deletion process.

    Returns:
        None
    """

    def mock_delete_category_exception(*args, **kwargs):
        raise Exception("Internal server error")

    category_dict = get_random_category_dict()
    category_instance = Categories(**category_dict)

    monkeypatch.setattr("sqlalchemy.orm.Query.first", mock_output(category_instance))
    monkeypatch.setattr("sqlalchemy.orm.Session.delete", mock_output())
    monkeypatch.setattr("sqlalchemy.orm.Session.commit", mock_delete_category_exception)

    response = client.delete(f"/categories/{category_dict['id']}")
    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error"}
