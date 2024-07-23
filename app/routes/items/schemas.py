from pydantic import BaseModel, StringConstraints, UUID4, ConfigDict
from typing import Annotated, List, Optional

from app.routes.category.schemas import CategoryRead


# Base Item schema
class ItemBase(BaseModel):
    name: Annotated[str, StringConstraints(min_length=1, max_length=255)]


# Item schema for Create operation
class ItemCreate(ItemBase):
    model_config = ConfigDict(from_attributes=True)

    category_ids: Optional[List[int]] = None


# Item schema for Update operation
class ItemUpdate(ItemBase):
    model_config = ConfigDict(from_attributes=True)
    
    category_ids: Optional[List[int]] = None


# Item schema for Read operation
class ItemRead(ItemBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: UUID4
    categories: List[CategoryRead] = []


class ItemDelete(BaseModel):
    id: int
