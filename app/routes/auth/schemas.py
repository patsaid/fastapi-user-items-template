"""
This module contains the schemas used for authentication routes.

- RefreshTokenRequestSchema: Schema for the request body of the refresh token endpoint.
- RefreshTokenResponseSchema: Schema for the response body of the refresh token endpoint.
- TokenData: Schema for the token data.
"""

from typing import Optional

from pydantic import UUID4, BaseModel

from app.commons.enums import TokenKind


class RefreshTokenRequestSchema(BaseModel):
    """
    Schema for the request to refresh a token.

    Attributes:
        refresh_token (str): The refresh token to be used for token refresh.
    """

    refresh_token: str


class RefreshTokenResponseSchema(BaseModel):
    """
    Represents the response schema for refreshing a token.

    Attributes:
        access_token (str): The refreshed access token.
        token_type (str): The type of the token.
    """

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """
    Represents the data contained in a token.

    Attributes:
        id (Optional[UUID4]): The ID associated with the token.
        exp (Optional[int]): The expiration time of the token.
        token_kind (Optional[TokenKind]): The kind of token.
    """

    id: Optional[UUID4]
    exp: Optional[int]
    token_kind: Optional[TokenKind]
