from pydantic import BaseModel, UUID4
from typing import Optional
from app.commons.enums import TokenKind


class RefreshTokenRequestSchema(BaseModel):
    refresh_token: str


class RefreshTokenResponseSchema(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[UUID4]
    exp: Optional[int]
    token_kind: Optional[TokenKind]
