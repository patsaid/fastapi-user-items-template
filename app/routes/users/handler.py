"""
This module contains the API handlers for the users endpoints
"""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.routes.auth.tokens import (
    create_access_token,
    create_refresh_token,
    get_current_user,
)
from app.routes.auth.utils import hash_pass, verify_password
from app.routes.users.models import Users
from app.routes.users.schemas import (
    LoginRequest,
    LoginResponse,
    SignUpResponse,
    UserCreate,
    UserRead,
)

logger = logging.getLogger("app")
user_router = APIRouter(prefix="/users", tags=["Users"])


@user_router.post("/signin", response_model=LoginResponse)
async def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """
    Logs in a user with the provided credentials.

    Args:
        payload (LoginRequest): The login request payload containing the username
            (or email) and password.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        LoginResponse: The login response containing the access token, refresh token,
            and token type.

    Raises:
        HTTPException: If the provided credentials are invalid.
    """

    # If username is provided, use it as email
    if payload.username is not None:
        payload.email = payload.username

    user = db.query(Users).filter(Users.email == payload.email).first()
    if not user:
        logger.warning("Login attempt with invalid email: %s", payload.email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials."
        )

    if not verify_password(payload.password, user.password):
        logger.warning(
            "Login attempt with invalid password for email: %s", payload.email
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials."
        )

    access_token = create_access_token(data={"id": user.id})
    refresh_token = create_refresh_token(data={"id": user.id})

    logger.info("User %s logged in successfully", user.id)

    return LoginResponse(
        access_token=access_token, refresh_token=refresh_token, token_type="bearer"
    )


@user_router.post(
    "/signup", status_code=status.HTTP_201_CREATED, response_model=SignUpResponse
)
async def signup(payload: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user.

    Args:
        payload (UserCreate): The user data to be created.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Raises:
        HTTPException: If a user with the same email already exists or if there is
            an internal server error.

    Returns:
        SignUpResponse: The response indicating that the user was created successfully.
    """
    existing_user = db.query(Users).filter(Users.email == payload.email).first()
    if existing_user:
        logger.warning("Signup attempt with existing email: %s", payload.email)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists.",
        )

    hashed_password = hash_pass(payload.password)
    payload.password = hashed_password

    user = Users(**payload.model_dump())
    db.add(user)

    try:
        db.commit()
        logger.info("User created successfully with email: %s", payload.email)
    except Exception as e:
        logger.error("Unexpected error while creating user: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong.",
        ) from e

    return SignUpResponse(detail="User created successfully.")


@user_router.get("/me")
async def get_me(user: Users = Depends(get_current_user)) -> UserRead:
    """
    Retrieve the current user's profile.

    Parameters:
    - user (Users): The current user.
    - db (Session): The database session.

    Returns:
    - UserRead: The user's profile.

    Raises:
    - HTTPException: If the user is not authenticated or the credentials are invalid.
    """
    if not user or (user.id is None):
        logger.warning("Invalid credentials provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials."
        )

    logger.info("User %s accessed their profile", user.id)

    return user


@user_router.get("/", response_model=List[UserRead])
async def read_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve a list of users with pagination.

    Parameters:
    - skip (int): The number of users to skip (default: 0)
    - limit (int): The maximum number of users to retrieve (default: 10)
    - current_user (Users): The current authenticated user
    - db (Session): The database session

    Returns:
    - List[UserRead]: A list of user objects with limited information (id, name, email, role)

    Raises:
    - HTTPException: If the current user is not an admin or if no users are found
    """

    # Ensure the current user is an admin
    if not current_user.is_active or current_user.role != "admin":
        logger.warning(
            "User %s attempted to read all users without sufficient permissions",
            current_user.id,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
        )

    # Get the users with pagination
    users = db.query(Users).offset(skip).limit(limit).all()
    if not users:
        logger.warning("No users found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No users found"
        )

    logger.info("%d users read by admin %s", len(users), current_user.id)

    # Return the users
    return [
        UserRead(id=user.id, name=user.name, email=user.email, role=user.role)
        for user in users
    ]
