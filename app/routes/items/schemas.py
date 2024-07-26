"""
Item schemas
This module contains the schemas for items.

It defines the following schemas:
- ItemBase: The base schema for an item.
- ItemCreate: The schema for creating a new item.
- ItemUpdate: The schema for updating an item.
- ItemRead: The schema for reading an item.
- ItemDelete: The schema for deleting an item.
"""

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.routes.category.schemas import CategoryRead


# Base Item schema
class ItemBase(BaseModel):
    """
    Represents the base schema for an item.
    """

    name: str = Field(..., min_length=1, max_length=255)


# Item schema for Create operation
class ItemCreate(ItemBase):
    """
    Represents the schema for creating an item.

    Attributes:
        category_ids (Optional[List[int]]): The list of category IDs
        associated with the item. Defaults to None.
    """

    model_config = ConfigDict(from_attributes=True)

    category_ids: Optional[List[int]] = None


# Item schema for Update operation
class ItemUpdate(ItemBase):
    """
    Represents the schema for updating an item.

    Attributes:
        category_ids (Optional[List[int]]): The list of category IDs
        associated with the item. Defaults to None.
    """

    model_config = ConfigDict(from_attributes=True)

    category_ids: Optional[List[int]] = None


# Item schema for Read operation
class ItemRead(ItemBase):
    """
    Represents an item read model.

    Attributes:
        id (int): The ID of the item.
        user_id (str): The ID of the user who owns the item.
        categories (List[CategoryRead]): The list of categories
        associated with the item.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: UUID
    categories: List[CategoryRead] = []


class ItemDelete(BaseModel):
    """
    Represents the schema for deleting an item.

    Attributes:
        id (int): The ID of the item to be deleted.
    """

    id: int
