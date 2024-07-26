"""
This module contains the models for categories and the association between categories and items.

The module defines the following classes:
- Categories: Represents a category in the database.
- Category_Item_association: Represents the association between a category and an item.

"""

from sqlalchemy import CheckConstraint, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


# pylint: disable=too-few-public-methods
class Categories(Base):
    """
    Represents a category in the database.

    Attributes:
        id (int): The unique identifier for the category.
        name (str): The name of the category, which must be unique and non-empty.
        items (relationship): A many-to-many relationship with `Items` through the
        `category_item_association` table.

    Constraints:
        - `name` must be unique across all categories.
        - `name` must have a length greater than 0.
    """

    __tablename__ = "categories"
    __table_args__ = (
        CheckConstraint("LENGTH(name) > 0", name="categories_name_length_check"),
        UniqueConstraint("name", name="categories_unique_name"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(36), nullable=False, unique=True)
    items = relationship(
        "Items", secondary="category_item_association", back_populates="categories"
    )


# pylint: disable=too-few-public-methods
class CategoryItemAssociation(Base):
    """
    Represents the association between a category and an item.

    Attributes:
        category_id (int): The identifier of the category.
        item_id (int): The identifier of the item.
    """

    __tablename__ = "category_item_association"

    category_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("categories.id"), primary_key=True
    )
    item_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("items.id"), primary_key=True
    )
