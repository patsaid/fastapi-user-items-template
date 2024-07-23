import pytest
from app.routes.auth.tokens import create_access_token
from app.routes.auth.utils import hash_pass
from app.routes.users.models import Users
from tests.factories.models_factory import get_random_user_dict

"""
- [ ] Test POST new user successfully
"""


def test_integrate_create_new_user_successful(client, db_session_integration):
    # Arrange: Prepare test data
    user_data = get_random_user_dict()
    user_data.pop("id")

    # Act: Make a POST request to create a new user
    response = client.post("/users/signup", json=user_data)
    body = response.json()

    # Assert: Verify response
    assert response.status_code == 201
    assert body == {"detail": "User created successfully."}

    # Assert: Verify the response and database state
    create_user = (
        db_session_integration.query(Users).filter_by(email=user_data["email"]).first()
    )
    assert create_user is not None

    # Ensure user details are correctly saved, but do not assert ID or other auto-generated fields
    assert create_user.email == user_data["email"]
    # Compare other relevant fields if necessary, but exclude password for security reasons


def test_integrate_login_successful(client, db_session_integration):
    # Arrange: Prepare test data
    user_data = get_random_user_dict()
    user_data.pop("id")
    plain_password = user_data["password"]
    hashed_password = hash_pass(user_data["password"])
    user_data["password"] = hashed_password
    new_user = Users(**user_data)
    db_session_integration.add(new_user)
    db_session_integration.commit()

    # Login data
    login_data = {"email": user_data["email"], "password": plain_password}

    # Act: Make a POST request to login
    response = client.post("/users/signin", json=login_data)
    body = response.json()

    # Assert: Verify response
    assert response.status_code == 200
    assert "access_token" in body
    assert "refresh_token" in body
    assert body["token_type"] == "bearer"

    # # Additional assertion: Verify that tokens can be decoded and are valid
    # # This is optional but useful to ensure tokens are correctly generated
    # import jwt
    # from app.auth.tokens import SECRET_KEY, ALGORITHM

    # try:
    #     decoded_access_token = jwt.decode(body["access_token"], SECRET_KEY, algorithms=[ALGORITHM])
    #     decoded_refresh_token = jwt.decode(body["refresh_token"], SECRET_KEY, algorithms=[ALGORITHM])
    #     assert decoded_access_token["id"] == new_user.id
    #     assert decoded_refresh_token["id"] == new_user.id
    # except jwt.ExpiredSignatureError:
    #     assert False, "Token has expired"
    # except jwt.InvalidTokenError:
    #     assert False, "Token is invalid"


def test_integrate_login_unsuccessful(client, db_session_integration):
    # Act: Make a POST request to login with invalid credentials
    login_data = {"email": "invalid@example.com", "password": "wrongpassword"}
    response = client.post("/users/signin", json=login_data)

    # Assert: Verify response
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid credentials."}


@pytest.fixture
def user_with_token(db_session_integration):
    # Arrange: Prepare test user data
    user_data = get_random_user_dict()
    user_data["role"] = "user"
    user_data["is_active"] = True
    user_data.pop("id")
    hashed_password = hash_pass(user_data["password"])
    user_data["password"] = hashed_password
    user = Users(**user_data)
    db_session_integration.add(user)
    db_session_integration.commit()

    # Create a token for the test user
    access_token = create_access_token(data={"id": user.id})
    return user, access_token


@pytest.fixture
def admin_user_with_token(db_session_integration):
    # Arrange: Prepare test user data
    user_data = get_random_user_dict()
    user_data["role"] = "admin"
    user_data["is_active"] = True
    user_data.pop("id")
    hashed_password = hash_pass(user_data["password"])
    user_data["password"] = hashed_password
    user = Users(**user_data)
    db_session_integration.add(user)
    db_session_integration.commit()

    # Create a token for the test user
    access_token = create_access_token(data={"id": user.id})
    return user, access_token


def test_integrate_get_me_successful(client, db_session_integration, user_with_token):
    user, access_token = user_with_token  # Unpack the user and access token

    # Act: Make a GET request to /me with valid token
    response = client.get(
        "/users/me", headers={"Authorization": f"Bearer {access_token}"}
    )
    body = response.json()

    # Assert: Verify response
    assert response.status_code == 200
    assert body["email"] == user.email


def test_integrate_get_me_unauthorized(client):
    # Act: Make a GET request to /me without token
    response = client.get("/users/me")

    # Assert: Verify response
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_integrate_read_users_successful(
    client, db_session_integration, admin_user_with_token
):
    user, access_token = admin_user_with_token  # Unpack the user and access token
    admin_user_email = user.email

    # Arrange: Prepare test data
    users = [Users(**get_random_user_dict()) for _ in range(5)]
    for user in users:
        user.password = hash_pass(user.password)
        db_session_integration.add(user)
    db_session_integration.commit()

    # Act: Make a GET request to /users/ with admin token
    response = client.get(
        "/users/", headers={"Authorization": f"Bearer {access_token}"}
    )
    body = response.json()

    # filter out the admin user in the body
    body = [user for user in body if user["email"] != admin_user_email]

    # Assert: Verify response
    assert response.status_code == 200
    assert len(body) == len(users)  # Additional user is the admin user
    assert all(user["email"] in [u.email for u in users] for user in body)


def test_integrate_read_users_unauthorized(client, user_with_token):
    user, access_token = user_with_token  # Unpack the user and access token

    # Act: Make a GET request to /users/ with regular user token
    response = client.get(
        "/users/", headers={"Authorization": f"Bearer {access_token}"}
    )

    # Assert: Verify response
    assert response.status_code == 403
    assert response.json() == {"detail": "Insufficient permissions"}
