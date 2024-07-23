from pydantic import BaseModel, ConfigDict, StringConstraints, EmailStr, UUID4
from typing import Annotated, Optional, List

from app.routes.items.schemas import ItemRead


# Base User schema
class UserBase(BaseModel):
    name: Annotated[str, StringConstraints(min_length=3, max_length=255)]
    email: EmailStr


# User schema for Create operation (SignUpRequest)
class UserCreate(UserBase):
    password: Annotated[str, StringConstraints(min_length=8, max_length=255)]


# User schema for Update operation
class UserUpdate(BaseModel):
    name: Optional[Annotated[str, StringConstraints(min_length=3, max_length=255)]] = (
        None
    )
    email: Optional[EmailStr] = None


# User schema for Read operation
class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    is_active: Optional[bool] = False
    role: str
    items: List["ItemRead"] = []  # Assuming User has many items


# Response schema for SignUp
class SignUpResponse(BaseModel):
    detail: str


# Request schema for Login
class LoginRequest(BaseModel):
    email: EmailStr
    username: Optional[str] = None
    password: Annotated[str, StringConstraints(min_length=8, max_length=255)]


# Response schema for Login
class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
