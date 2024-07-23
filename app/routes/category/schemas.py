from pydantic import BaseModel, StringConstraints, ConfigDict, UUID4
from typing import Annotated, Optional


# Base Category schema
class CategoryBase(BaseModel):
    name: Annotated[str, StringConstraints(min_length=1, max_length=255)]


# Category schema for Create operation
class CategoryCreate(CategoryBase):
    pass

# Category schema for associate operation
class CategoryAssociate(BaseModel):
    category_id: int


# Category schema for Update operation
class CategoryUpdate(CategoryBase):
    name: Optional[Annotated[str, StringConstraints(min_length=1, max_length=255)]]


# Category schema for Read operation
class CategoryRead(CategoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


# Category schema for Delete operation
class CategoryDelete(BaseModel):
    id: int
