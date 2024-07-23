from app.routes.category.models import Categories


def test_integrate_create_category_successful(client, db_session_integration, auth_header):
    # Arrange: Prepare payload
    payload = {"name": "Test Category"}

    # Act: Make a POST request to create category
    response = client.post("/categories/", json=payload, headers=auth_header)

    # Assert: Verify response
    assert response.status_code == 201
    response_data = response.json()
    assert response_data["name"] == payload["name"]

def test_integrate_read_category_successful(client, db_session_integration, auth_header, admin_user):
    # Arrange: Create a category
    category = Categories(name="Test Category")
    db_session_integration.add(category)
    db_session_integration.commit()

    # Act: Make a GET request to read the category
    response = client.get(f"/categories/{category.id}", headers=auth_header)

    # Assert: Verify response
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["id"] == category.id
    assert response_data["name"] == category.name

def test_integrate_update_category_successful(client, db_session_integration, auth_header, admin_user):
    # Arrange: Create a category
    category = Categories(name="Old Category")
    db_session_integration.add(category)
    db_session_integration.commit()

    # Prepare payload
    payload = {"name": "Updated Category"}

    # Act: Make a PUT request to update the category
    response = client.put(f"/categories/{category.id}", json=payload, headers=auth_header)

    # Assert: Verify response
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["name"] == payload["name"]

def test_integrate_delete_category_successful(client, db_session_integration, auth_header, admin_user):
    # Arrange: Create a category
    category = Categories(name="Test Category")
    db_session_integration.add(category)
    db_session_integration.commit()

    # Act: Make a DELETE request to delete the category
    response = client.delete(f"/categories/{category.id}", headers=auth_header)

    # Assert: Verify response
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["id"] == category.id

def test_integrate_read_all_categories_successful(client, db_session_integration, auth_header, admin_user):
    # Arrange: Create multiple categories
    categories = [
        Categories(name="Category 1"),
        Categories(name="Category 2")
    ]
    db_session_integration.add_all(categories)
    db_session_integration.commit()

    # Act: Make a GET request to read all categories
    response = client.get("/categories/", headers=auth_header)

    # Assert: Verify response
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data) == len(categories)
    assert response_data[0]["name"] == categories[0].name
    assert response_data[1]["name"] == categories[1].name
