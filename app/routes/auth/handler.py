"""
This module contains the authentication routes and handlers for the FastAPI application.

It includes the following routes:
- /auth/refresh-token: Refreshes an access token using a refresh token.
- /auth/token: Authenticates a user and returns an access token.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.commons.enums import TokenKind
from app.db.database import get_db
from app.routes.auth.schemas import (
    RefreshTokenRequestSchema,
    RefreshTokenResponseSchema,
    TokenData,
)
from app.routes.auth.tokens import create_access_token, verify_token
from app.routes.auth.utils import verify_password
from app.routes.users.models import Users

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post("/refresh-token", response_model=RefreshTokenResponseSchema)
def refresh_token(payload: RefreshTokenRequestSchema):
    """
    Refreshes an access token using a refresh token.

    Args:
        payload (RefreshTokenRequestSchema): The request payload containing the refresh token.

    Returns:
        RefreshTokenResponseSchema: The response containing the new access token and token type.
    """
    credentials_exception = HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid Token")
    token_data: TokenData = verify_token(payload.refresh_token, credentials_exception)

    if token_data.token_kind != TokenKind.RefreshToken:
        raise credentials_exception

    access_token = create_access_token(data={"id": token_data.id})

    return RefreshTokenResponseSchema(access_token=access_token, token_type="bearer")


@auth_router.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """
    Authenticates a user and returns an access token.

    Args:
        form_data (OAuth2PasswordRequestForm, optional): The form data containing
            the username and password. Defaults to Depends().
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        dict: The response containing the access token and token type.
    """
    email = form_data.username
    password = form_data.password

    user = db.query(Users).filter(Users.email == email).first()
    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}
