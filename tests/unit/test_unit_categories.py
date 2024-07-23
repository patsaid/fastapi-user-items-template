import pytest
from app.routes.category.models import Categories
from tests.factories.models_factory import get_random_category_dict
from unittest.mock import MagicMock

def mock_output(return_value=None):
    return lambda *args, **kwargs: return_value


"""
- [ ] Test POST create category successfully
"""
def test_unit_create_category_successfully(client, mock_admin_user, mock_db_operations, monkeypatch):
    category_dict = get_random_category_dict()
    category_instance = Categories(**category_dict)

    monkeypatch.setattr("sqlalchemy.orm.Query.first", lambda *args, **kwargs: category_instance)

    payload = category_dict.copy()
    payload.pop("id")
    response = client.post("/categories", json=payload)
    
    response_payload = response.json()
    expected_payload = category_dict.copy()
    expected_payload["id"] = 1  # Ensure ID is correctly assigned
    
    assert response.status_code == 201
    assert response_payload == expected_payload

"""
- [ ] Test POST create category internal server error
"""
def test_unit_create_category_internal_error(client, mock_admin_user, monkeypatch):
    category_dict = get_random_category_dict()
    category_instance = Categories(**category_dict)
    
    def mock_create_category_exception(*args, **kwargs):
        raise Exception("Internal server error")

    mock_session = MagicMock()
    mock_session.add = MagicMock()
    mock_session.commit = mock_create_category_exception
    mock_session.refresh = MagicMock()

    monkeypatch.setattr("app.db.database.get_db", lambda: mock_session)
    
    payload = category_dict.copy()
    payload.pop("id")
    
    response = client.post("/categories", json=payload)
    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error"}

"""
- [ ] Test PUT update category successfully
"""
def test_unit_update_category_successfully(client, mock_admin_user, monkeypatch):
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

"""
- [ ] Test PUT update category not found
"""
def test_unit_update_category_not_found(client, mock_admin_user, monkeypatch):
    category_dict = get_random_category_dict()

    monkeypatch.setattr("sqlalchemy.orm.Query.first", mock_output())
    monkeypatch.setattr("sqlalchemy.orm.Session.commit", mock_output())
    monkeypatch.setattr("sqlalchemy.orm.Session.refresh", mock_output())

    body = category_dict.copy()
    body.pop("id")
    response = client.put(f"/categories/{category_dict['id']}", json=body)
    assert response.status_code == 404
    assert response.json() == {"detail": "Category not found"}

"""
- [ ] Test PUT update category internal server error
"""
def test_unit_update_category_internal_error(client, mock_admin_user, monkeypatch):
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

"""
- [ ] Test GET single category by id successfully
"""
@pytest.mark.parametrize("category", [get_random_category_dict() for _ in range(3)])
def test_unit_get_single_category_successfully(client, monkeypatch, category):
    monkeypatch.setattr("sqlalchemy.orm.Query.first", mock_output(Categories(**category)))
    response = client.get(f"/categories/{category['id']}")

    assert response.status_code == 200
    assert response.json() == category

"""
- [ ] Test GET single category by id not found
"""
@pytest.mark.parametrize("category", [get_random_category_dict() for _ in range(3)])
def test_unit_get_single_category_not_found(client, monkeypatch, category):
    monkeypatch.setattr("sqlalchemy.orm.Query.first", mock_output())
    response = client.get(f"/categories/{category['id']}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Category not found"}

"""
- [ ] Test DELETE category successfully
"""
def test_unit_delete_category_successfully(client, mock_admin_user, monkeypatch):
    category_dict = get_random_category_dict()
    category_instance = Categories(**category_dict)

    monkeypatch.setattr("sqlalchemy.orm.Query.first", mock_output(category_instance))
    monkeypatch.setattr("sqlalchemy.orm.Session.delete", mock_output())
    monkeypatch.setattr("sqlalchemy.orm.Session.commit", mock_output())

    response = client.delete(f"/categories/{category_dict['id']}")

    assert response.status_code == 200
    assert response.json() == {"id": category_dict["id"]}

"""
- [ ] Test DELETE category not found
"""
def test_unit_delete_category_not_found(client, mock_admin_user, monkeypatch):
    monkeypatch.setattr("sqlalchemy.orm.Query.first", mock_output())
    monkeypatch.setattr("sqlalchemy.orm.Session.commit", mock_output())

    response = client.delete("/categories/1")
    assert response.status_code == 404
    assert response.json() == {"detail": "Category not found"}

"""
- [ ] Test DELETE category internal server error
"""
def test_unit_delete_category_internal_error(client, mock_admin_user, monkeypatch):
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