import logging
from typing import List

from app.routes.category.models import Categories
from app.routes.items.models import Items
from fastapi import Depends, HTTPException, Query, status, APIRouter
from app.routes.items.schemas import ItemCreate, ItemRead, ItemUpdate, ItemDelete
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.routes.auth.tokens import get_current_user
from app.routes.users.models import Users

logger = logging.getLogger("app")
items_router = APIRouter(prefix="/items", tags=["Items"])


@items_router.post("/", response_model=ItemRead, status_code=status.HTTP_201_CREATED)
async def create_items(
    payload: ItemCreate,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    This API is used to create items
    """

    # Ensure the current user is active
    if not current_user.is_active:
        logger.warning(f"Inactive user {current_user.id} attempted to create an item")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user"
        )

    # Check if all categories exist
    if payload.category_ids:
        categories = (
            db.query(Categories).filter(Categories.id.in_(payload.category_ids)).all()
        )
        if len(categories) != len(payload.category_ids):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="One or more categories not found",
            )

    # Create a new item instance
    new_item = Items(
        user_id=current_user.id,  # Assign the current user's ID
        name=payload.name,
        categories=categories if payload.category_ids else [],
    )

    # Add the new item to the session
    db.add(new_item)

    try:
        # Commit the transaction
        db.commit()
        # Refresh to get the latest state of the item (e.g., auto-generated fields)
        db.refresh(new_item)
        logger.info(f"Item {new_item.id} created by user {current_user.id}")
    except Exception as e:
        # Rollback in case of error
        db.rollback()
        logger.error(f"Error creating item for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error"
        )

    # Return the newly created item
    return new_item


@items_router.put("/{item_id}", response_model=ItemRead)
async def update_items(
    item_id: int,
    payload: ItemUpdate,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    This API is used to update items
    """

    # Ensure the current user is active
    if not current_user.is_active:
        logger.warning(
            f"Inactive user {current_user.id} attempted to update item {item_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user"
        )

    # Check if all categories exist
    if payload.category_ids:
        categories = (
            db.query(Categories).filter(Categories.id.in_(payload.category_ids)).all()
        )
        if len(categories) != len(payload.category_ids):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="One or more categories not found",
            )

    # Get the item instance
    item = (
        db.query(Items)
        .filter(Items.id == item_id)
        .filter(Items.user_id == current_user.id)
        .first()
    )
    if not item:
        logger.warning(f"Item {item_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )

    # Update the item fields
    item.name = payload.name
    item.categories = categories if payload.category_ids else []

    try:
        # Commit the transaction
        db.commit()
        # Refresh to get the latest state of the item (e.g., auto-generated fields)
        db.refresh(item)

        logger.info(f"Item {item.id} updated by user {current_user.id}")
    except Exception as e:
        # Rollback in case of error
        db.rollback()
        logger.error(f"Error updating item {item_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error"
        )

    # Return the updated item
    return item


@items_router.get("/{item_id}", response_model=ItemRead)
async def read_items(
    item_id: int,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    This API is used to read items
    """

    # Get the item instance
    item = (
        db.query(Items)
        .filter(Items.id == item_id)
        .filter(Items.user_id == current_user.id)
        .first()
    )
    if not item:
        logger.warning(f"Item {item_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )

    # Log the successful retrieval of the item
    logger.info(f"Item {item_id} retrieved by user {current_user.id}")

    # Return the item
    return item


@items_router.get("/", response_model=List[ItemRead])
async def read_all_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    This API is used to read all items with optional pagination
    """

    # Ensure the current user is active
    if not current_user.is_active:
        logger.warning(f"Inactive user {current_user.id} attempted to read items")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user"
        )

    # Filter items based on user role
    if current_user.role == "admin":
        items_query = db.query(Items)
    else:
        items_query = db.query(Items).filter(Items.user_id == current_user.id)

    # Apply pagination
    items = items_query.offset(skip).limit(limit).all()

    # If no items found, raise a 404 error
    if not items:
        logger.warning("No items found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No items found"
        )

    logger.info(f"{len(items)} items read by user {current_user.id}")

    # Return the items
    return [
        ItemRead(id=item.id, name=item.name, user_id=item.user_id) for item in items
    ]


@items_router.delete("/{item_id}", response_model=ItemDelete)
async def delete_items(
    item_id: int,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    This API is used to delete items
    """

    # Ensure the current user is active
    if not current_user.is_active:
        logger.warning(
            f"Inactive user {current_user.id} attempted to delete item {item_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user"
        )

    # Get the item instance
    item = (
        db.query(Items)
        .filter(Items.id == item_id)
        .filter(Items.user_id == current_user.id)
        .first()
    )
    if not item:
        logger.warning(f"Item {item_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )

    # Delete the item
    db.delete(item)

    try:
        # Commit the transaction
        db.commit()
        logger.info(f"Item {item_id} deleted by user {current_user.id}")
    except Exception as e:
        # Rollback in case of error
        db.rollback()
        logger.error(f"Error deleting item {item_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error"
        )

    # Return the deleted item ID
    return ItemDelete(id=item.id)
