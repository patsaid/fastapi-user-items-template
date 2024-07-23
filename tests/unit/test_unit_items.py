import pytest
from app.routes.items.models import Items
from tests.factories.models_factory import get_random_item_dict

def mock_output(return_value=None):
    return lambda *args, **kwargs: return_value

def test_unit_create_item_successfully(client, monkeypatch, mock_admin_user, mock_db_operations):
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

def test_unit_create_item_internal_error(client, monkeypatch, mock_admin_user, mock_db_operations_exception):
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

def test_unit_update_item_successfully(client, mock_admin_user, monkeypatch, mock_db_operations):
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

def test_unit_update_item_not_found(client, mock_admin_user, monkeypatch):
    item_dict = get_random_item_dict()
    item_dict["user_id"] = mock_admin_user["id"]
    item_dict.pop("categories")

    monkeypatch.setattr("sqlalchemy.orm.Query.first", mock_output())

    body = item_dict.copy()
    body.pop("id")
    response = client.put(f"/items/{item_dict['id']}", json=body)
    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found"}

def test_unit_update_item_internal_error(client, mock_admin_user, monkeypatch):
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
def test_unit_get_single_item_successfully(client, monkeypatch, item):
    item.pop("categories")
    
    monkeypatch.setattr("sqlalchemy.orm.Query.first", mock_output(Items(**item)))
    response = client.get(f"/items/{item['id']}")
    response_payload = response.json()
    response_payload.pop("categories") 
    
    assert response.status_code == 200
    assert response_payload == item

@pytest.mark.parametrize("item", [get_random_item_dict() for _ in range(3)])
def test_unit_get_single_item_not_found(client, monkeypatch, item):
    monkeypatch.setattr("sqlalchemy.orm.Query.first", mock_output())
    response = client.get(f"/items/{item['id']}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found"}

def test_unit_delete_item_successfully(client, mock_admin_user, monkeypatch):
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

def test_unit_delete_item_not_found(client, mock_admin_user, monkeypatch):
    monkeypatch.setattr("sqlalchemy.orm.Query.first", mock_output())
    monkeypatch.setattr("sqlalchemy.orm.Session.commit", mock_output())

    response = client.delete("/items/1")
    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found"}

def test_unit_delete_item_internal_error(client, mock_admin_user, monkeypatch):
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
