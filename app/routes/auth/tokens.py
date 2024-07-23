from datetime import timedelta, datetime
from app.routes.auth.schemas import TokenData
from app.core.config import (
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
    JWT_SECRET_KEY,
    JWT_ALGORITHM,
    JWT_REFRESH_TOKEN_EXPIRE_MINUTES,
)
from app.db.database import get_db
from sqlalchemy.orm import Session
from app.routes.users.models import Users
from fastapi import Depends, HTTPException, status
from jose import jwt
from fastapi.security import OAuth2PasswordBearer
from app.commons.enums import TokenKind
from uuid import UUID


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def create_access_token(data: dict):
    to_encode = data.copy()

    # Convert UUID to string if present in data
    if "id" in to_encode and isinstance(to_encode["id"], UUID):
        to_encode["id"] = str(to_encode["id"])

    expire = datetime.now() + timedelta(minutes=int(JWT_ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update(
        {"exp": int(expire.timestamp()), "token_kind": TokenKind.AccessToken.value}
    )

    return jwt.encode(to_encode, JWT_SECRET_KEY, JWT_ALGORITHM)


def create_refresh_token(data: dict):
    to_encode = data.copy()
    
    if "id" in to_encode and isinstance(to_encode["id"], UUID):
        to_encode["id"] = str(to_encode["id"])

    expire = datetime.now() + timedelta(minutes=int(JWT_REFRESH_TOKEN_EXPIRE_MINUTES))
    to_encode.update(
        {"exp": int(expire.timestamp()), "token_kind": TokenKind.RefreshToken.value}
    )

    return jwt.encode(to_encode, JWT_SECRET_KEY, JWT_ALGORITHM)


def verify_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=JWT_ALGORITHM)

        id: str = payload.get("id")
        if id is None:
            raise credentials_exception

        # Create TokenData instance using only necessary fields
        token_data = TokenData(
            id=id, exp=payload.get("exp"), token_kind=payload.get("token_kind")
        )
    except jwt.JWTError:
        raise credentials_exception

    return token_data


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):  
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = verify_token(token, credentials_exception)
    user = db.query(Users).filter(Users.id == token.id).first()

    return user
