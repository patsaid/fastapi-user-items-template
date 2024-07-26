"""
This module contains the SQLAlchemy model for the Users table.

It defines the following model:
- Users: Represents a user in the system.

"""

import uuid

from sqlalchemy import Boolean, CheckConstraint, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.commons.utils import get_uuid
from app.db.database import Base


# pylint: disable=too-few-public-methods
class Users(Base):
    """
    Represents a user in the system.

    Attributes:
        id (uuid.UUID): The unique identifier for the user.
        name (str): The name of the user.
        email (str): The email address of the user.
        password (str): The password of the user.
        is_active (bool): Indicates whether the user is active or not.
        role (str): The role of the user (e.g., 'user', 'admin').
        items (List[Items]): The items associated with the user.
    """

    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("LENGTH(name) >= 3", name="users_name_length_check"),
        CheckConstraint("LENGTH(email) >= 1", name="users_email_length_check"),
        CheckConstraint("LENGTH(password) >= 8", name="users_password_length_check"),
        CheckConstraint("role IN ('user', 'admin')", name="users_role_validity_check"),
        UniqueConstraint("email", name="users_unique_email"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=get_uuid
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255), index=True, unique=True, nullable=False
    )
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )
    role = mapped_column(String(50), nullable=False, default="user")

    # Relationship to Items
    items = relationship("Items", back_populates="user", cascade="all, delete-orphan")
