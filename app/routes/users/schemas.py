"""
This module contains the schemas for the User model.

It defines the following schemas:
- UserBase: The base schema for a user.
- UserCreate: The schema for creating a new user.
- UserUpdate: The schema for updating a user.
- UserRead: The schema for reading a user.
- SignUpResponse: The response schema for the SignUp API.
- LoginRequest: The request schema for the Login API.
- LoginResponse: The response schema for the Login API.
"""

from typing import Annotated, List, Optional

from pydantic import UUID4, BaseModel, ConfigDict, EmailStr, StringConstraints

from app.routes.items.schemas import ItemRead


# Base User schema
class UserBase(BaseModel):
    """
    Represents the base schema for a user.

    Attributes:
        name (str): The name of the user. Must be between 3 and 255 characters long.
        email (EmailStr): The email address of the user.
    """

    name: Annotated[str, StringConstraints(min_length=3, max_length=255)]
    email: EmailStr


# User schema for Create operation (SignUpRequest)
class UserCreate(UserBase):
    """
    Represents the schema for creating a user.

    Attributes:
        password (str): The password for the user. Must be between 8
            and 255 characters long.
    """

    password: Annotated[str, StringConstraints(min_length=8, max_length=255)]


# User schema for Update operation
class UserUpdate(BaseModel):
    """
    Represents the schema for updating user information.

    Attributes:
        name (Optional[str]): The updated name of the user. Must be between 3
            and 255 characters long.
        email (Optional[EmailStr]): The updated email address of the user.
    """

    name: Optional[Annotated[str, StringConstraints(min_length=3, max_length=255)]] = (
        None
    )
    email: Optional[EmailStr] = None


# User schema for Read operation
class UserRead(UserBase):
    """
    Represents a user with read-only properties.

    Attributes:
        id (UUID4): The unique identifier of the user.
        is_active (bool, optional): Indicates whether the user is active or not. Defaults to False.
        role (str): The role of the user.
        items (List[ItemRead], optional): The list of items associated with the user.
            Defaults to an empty list.
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    is_active: Optional[bool] = False
    role: str
    items: List["ItemRead"] = []  # Assuming User has many items


# Response schema for SignUp
class SignUpResponse(BaseModel):
    """
    Represents the response data for a sign-up request.

    Attributes:
        detail (str): A message providing details about the sign-up request.
    """

    detail: str


# Request schema for Login
class LoginRequest(BaseModel):
    """
    Represents the request schema for user login.

    Attributes:
        email (EmailStr): The email address of the user.
        username (Optional[str]): The username of the user (optional).
        password (Annotated[str, StringConstraints(min_length=8,
            max_length=255)]): The password of the user.
    """

    email: EmailStr
    username: Optional[str] = None
    password: Annotated[str, StringConstraints(min_length=8, max_length=255)]


# Response schema for Login
class LoginResponse(BaseModel):
    """
    Represents the response returned when a user logs in.

    Attributes:
        access_token (str): The access token for the logged-in user.
        refresh_token (str): The refresh token for the logged-in user.
        token_type (str): The type of the access token.
    """

    access_token: str
    refresh_token: str
    token_type: str
