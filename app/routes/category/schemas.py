"""
Category Schemas
This module contains the schemas for the category routes in the FastAPI application.

It defines the following schemas:
- CategoryBase: The base schema for a category.
- CategoryCreate: The schema for creating a new category.
- CategoryAssociate: The schema for associating a category with another entity.
- CategoryUpdate: The schema for updating a category.
- CategoryRead: The schema for reading a category.
- CategoryDelete: The schema for deleting a category.
"""

from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict, StringConstraints


# Base Category schema
class CategoryBase(BaseModel):
    """
    Represents the base schema for a category.

    Attributes:
        name (str): The name of the category.
    """

    name: Annotated[str, StringConstraints(min_length=1, max_length=255)]


# Category schema for Create operation
class CategoryCreate(CategoryBase):
    """
    Represents the schema for creating a new category.

    Inherits from `CategoryBase` which contains the common properties for a category.

    Attributes:
        Inherits all attributes from `CategoryBase`.

    """


# Category schema for associate operation
class CategoryAssociate(BaseModel):
    """
    Represents the association between a category and another entity.
    """

    category_id: int


# Category schema for Update operation
class CategoryUpdate(CategoryBase):
    """
    Represents the schema for updating a category.

    Attributes:
        name (Optional[str]): The updated name of the category. Must be a string
        with a minimum length of 1 and a maximum length of 255.
    """

    name: Optional[Annotated[str, StringConstraints(min_length=1, max_length=255)]]


# Category schema for Read operation
class CategoryRead(CategoryBase):
    """
    Represents a category read model.

    Attributes:
        id (int): The ID of the category.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int


# Category schema for Delete operation
class CategoryDelete(BaseModel):
    """
    Represents the schema for deleting a category.

    Attributes:
        id (int): The ID of the category to be deleted.
    """

    id: int
