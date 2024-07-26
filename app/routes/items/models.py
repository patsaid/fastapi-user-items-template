"""
This module defines the Items model for the application.

The Items model represents an item in the system. It is associated with a
user and can belong to multiple categories.

Attributes:
    id (int): The unique identifier for the item.
    user_id (uuid.UUID): The ID of the user who owns the item.
    name (str): The name of the item.
    categories (List[Categories]): The categories that the item belongs to.
    user (Users): The user who owns the item.

"""

import uuid

from sqlalchemy import CheckConstraint, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


# pylint: disable=too-few-public-methods
class Items(Base):
    """
    Represents an item in the system.

    Attributes:
        id (int): The unique identifier for the item.
        user_id (uuid.UUID): The ID of the user who owns the item.
        name (str): The name of the item.
        categories (List[Categories]): The categories associated with the item.
        user (Users): The user who owns the item.
    """

    __tablename__ = "items"
    __table_args__ = (
        CheckConstraint("LENGTH(name) > 0", name="items_name_length_check"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Relationship to Categories
    categories = relationship(
        "Categories", secondary="category_item_association", back_populates="items"
    )

    # Relationship to Users
    user = relationship("Users", back_populates="items")
