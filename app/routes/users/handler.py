import logging
from typing import List

from app.routes.users.models import Users
from fastapi import Depends, HTTPException, Query, status, APIRouter
from app.routes.users.schemas import (
    UserCreate,
    SignUpResponse,
    LoginRequest,
    LoginResponse,
    UserRead,
)
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.routes.auth.utils import verify_password, hash_pass
from app.routes.auth.tokens import create_access_token, create_refresh_token, get_current_user

logger = logging.getLogger("app")
user_router = APIRouter(prefix="/users", tags=["Users"])


@user_router.post("/signin", response_model=LoginResponse)
async def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """
    This API is used to login users to the application
    """

    # If username is provided, use it as email        
    if payload.username is not None:
        payload.email = payload.username

    user = db.query(Users).filter(Users.email == payload.email).first()
    if not user:
        logger.warning(f"Login attempt with invalid email: {payload.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials."
        )

    if not verify_password(payload.password, user.password):
        logger.warning(
            f"Login attempt with invalid password for email: {payload.email}"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials."
        )

    access_token = create_access_token(data={"id": user.id})
    refresh_token = create_refresh_token(data={"id": user.id})

    logger.info(f"User {user.id} logged in successfully")

    return LoginResponse(
        access_token=access_token, refresh_token=refresh_token, token_type="bearer"
    )


@user_router.post(
    "/signup", status_code=status.HTTP_201_CREATED, response_model=SignUpResponse
)
async def signup(payload: UserCreate, db: Session = Depends(get_db)):
    """
    This API is used to signup users to the application
    """
    existing_user = db.query(Users).filter(Users.email == payload.email).first()
    if existing_user:
        logger.warning(f"Signup attempt with existing email: {payload.email}")
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
        logger.info(f"User created successfully with email: {payload.email}")
    except Exception as e:
        logger.error(f"Unexpected error while creating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong.",
        )

    return SignUpResponse(detail="User created successfully.")


@user_router.get("/me")
async def get_me(
    user: Users = Depends(get_current_user), db: Session = Depends(get_db)
) -> UserRead:
    if not user or (user.id is None):
        logger.warning("Invalid credentials provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials."
        )

    logger.info(f"User {user.id} accessed their profile")

    return user


@user_router.get("/", response_model=List[UserRead])
async def read_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    This API is used to read all users with optional pagination
    """

    # Ensure the current user is an admin
    if not current_user.is_active or current_user.role != "admin":
        logger.warning(
            f"User {current_user.id} attempted to read all users without sufficient permissions"
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

    logger.info(f"{len(users)} users read by admin {current_user.id}")

    # Return the users
    return [
        UserRead(id=user.id, name=user.name, email=user.email, role=user.role)
        for user in users
    ]
