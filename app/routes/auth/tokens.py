"""
This module contains functions related to token generation, verification, and user authentication.

Functions:
- create_access_token(data: dict) -> str: Generates an access token based on the provided data.
- create_refresh_token(data: dict) -> str: Generates a refresh token based on the provided data.
- verify_token(token: str, credentials_exception) -> TokenData: Verifies the validity of a token
    and returns the corresponding TokenData.
- get_current_user(token: str, db: Session) -> Users: Retrieves the current user based on the
    provided token and database session.
"""

from datetime import datetime, timedelta
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from sqlalchemy.orm import Session

from app.commons.enums import TokenKind
from app.core.config import (
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
    JWT_ALGORITHM,
    JWT_REFRESH_TOKEN_EXPIRE_MINUTES,
    JWT_SECRET_KEY,
)
from app.db.database import get_db
from app.routes.auth.schemas import TokenData
from app.routes.users.models import Users

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def create_access_token(data: dict):
    """
    Create an access token based on the provided data.

    Args:
        data (dict): The data to be encoded into the access token.

    Returns:
        str: The encoded access token.
    """
    to_encode = data.copy()

    # Convert UUID to string if present in data
    if "id" in to_encode and isinstance(to_encode["id"], UUID):
        to_encode["id"] = str(to_encode["id"])

    expire = datetime.now() + timedelta(minutes=int(JWT_ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update(
        {"exp": int(expire.timestamp()), "token_kind": TokenKind.ACCESS_TOKEN.value}
    )

    return jwt.encode(to_encode, JWT_SECRET_KEY, JWT_ALGORITHM)


def create_refresh_token(data: dict):
    """
    Create a refresh token.

    Args:
        data (dict): The data to be encoded in the token.

    Returns:
        str: The encoded refresh token.
    """
    to_encode = data.copy()

    if "id" in to_encode and isinstance(to_encode["id"], UUID):
        to_encode["id"] = str(to_encode["id"])

    expire = datetime.now() + timedelta(minutes=int(JWT_REFRESH_TOKEN_EXPIRE_MINUTES))
    to_encode.update(
        {"exp": int(expire.timestamp()), "token_kind": TokenKind.REFESH_TOKEN.value}
    )

    return jwt.encode(to_encode, JWT_SECRET_KEY, JWT_ALGORITHM)


def verify_token(token: str, credentials_exception):
    """
    Verify the authenticity of a token and extract the necessary information.

    Args:
        token (str): The token to be verified.
        credentials_exception: An exception to be raised if the token is invalid.

    Returns:
        TokenData: An instance of TokenData containing the extracted information from the token.

    Raises:
        credentials_exception: If the token is invalid or does not contain the necessary
            information.
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=JWT_ALGORITHM)

        user_id: str = payload.get("id")
        if id is None:
            raise credentials_exception

        # Create TokenData instance using only necessary fields
        token_data = TokenData(
            id=user_id, exp=payload.get("exp"), token_kind=payload.get("token_kind")
        )
    except jwt.JWTError:
        raise credentials_exception

    return token_data


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    """
    Retrieves the current user based on the provided token.

    Args:
        token (str): The authentication token.
        db (Session): The database session.

    Returns:
        User: The current user.

    Raises:
        HTTPException: If the credentials cannot be validated.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = verify_token(token, credentials_exception)
    user = db.query(Users).filter(Users.id == token.id).first()

    return user
