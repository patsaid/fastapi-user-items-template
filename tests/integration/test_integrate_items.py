import pytest
from app.routes.auth.tokens import create_access_token
from app.routes.auth.utils import hash_pass
from app.routes.users.models import Users
from app.routes.items.models import Items
from app.routes.category.models import Categories
from tests.factories.models_factory import get_random_user_dict

@pytest.fixture
def active_user(db_session_integration):
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
def access_token(active_user):
    return create_access_token(data={"id": active_user.id})

@pytest.fixture
def auth_header(access_token):
    return {"Authorization": f"Bearer {access_token}"}


def test_integrate_create_item_successful(client, db_session_integration, auth_header):
    # Arrange: Create a category
    category = Categories(name="Test Category")
    db_session_integration.add(category)
    db_session_integration.commit()

    # Prepare payload
    payload = {
        "name": "Test Item",
        "category_ids": [category.id]
    }

    # Act: Make a POST request to create item
    response = client.post("/items/", json=payload, headers=auth_header)

    # Assert: Verify response
    assert response.status_code == 201
    response_data = response.json()
    assert response_data["name"] == payload["name"]
    assert response_data["categories"][0]["id"] == category.id

def test_integrate_read_item_successful(client, db_session_integration, auth_header, active_user):
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

def test_integrate_update_item_successful(client, db_session_integration, auth_header, active_user):
    # Arrange: Create an item and category
    item = Items(name="Old Item", user_id=active_user.id)
    category = Categories(name="New Category")
    db_session_integration.add_all([item, category])
    db_session_integration.commit()

    # Prepare payload
    payload = {
        "name": "Updated Item",
        "category_ids": [category.id]
    }

    # Act: Make a PUT request to update the item
    response = client.put(f"/items/{item.id}", json=payload, headers=auth_header)

    # Assert: Verify response
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["name"] == payload["name"]
    assert response_data["categories"][0]["id"] == category.id

def test_integrate_delete_item_successful(client, db_session_integration, auth_header, active_user):
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

def test_integrate_read_all_items_successful(client, db_session_integration, auth_header, active_user):
    # Arrange: Create multiple items
    items = [
        Items(name="Item 1", user_id=active_user.id),
        Items(name="Item 2", user_id=active_user.id)
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