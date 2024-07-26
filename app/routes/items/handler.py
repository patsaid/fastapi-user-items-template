"""
This module contains the API handlers for the items endpoints
"""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.routes.auth.tokens import get_current_user
from app.routes.category.models import Categories
from app.routes.items.models import Items
from app.routes.items.schemas import ItemCreate, ItemDelete, ItemRead, ItemUpdate
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
    Create a new item.

    Args:
        payload (ItemCreate): The payload containing the item details.
        current_user (Users, optional): The current user. Defaults to Depends(get_current_user).
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        Items: The newly created item.

    Raises:
        HTTPException: If the current user is inactive, one or more categories are not found,
            or an internal server error occurs.
    """

    # Ensure the current user is active
    if not current_user.is_active:
        logger.warning("Inactive user %s attempted to create an item", current_user.id)
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
        logger.info("Item %s created by user %s", new_item.id, current_user.id)
    except Exception as e:
        # Rollback in case of error
        db.rollback()
        logger.error("Error creating item for user %s: %s", current_user.id, e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        ) from e

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
    Update an item with the given item_id and payload.

    Parameters:
    - item_id (int): The ID of the item to be updated.
    - payload (ItemUpdate): The updated item data.
    - current_user (Users, optional): The current user. Defaults to the result of
        the get_current_user function.
    - db (Session, optional): The database session. Defaults to the result of the get_db function.

    Returns:
    - item (Items): The updated item.

    Raises:
    - HTTPException: If the current user is inactive, the item is not found, or there is
        an internal server error.
    - HTTPException: If one or more categories specified in the payload are not found.

    """

    # Ensure the current user is active
    if not current_user.is_active:
        logger.warning(
            "Inactive user %s attempted to update item %s", current_user.id, item_id
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
        logger.warning("Item %s not found", item_id)
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

        logger.info("Item %s updated by user %s", item.id, current_user.id)
    except Exception as e:
        # Rollback in case of error
        db.rollback()
        logger.error("Error updating item %s: %s", item_id, e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        ) from e

    # Return the updated item
    return item


@items_router.get("/{item_id}", response_model=ItemRead)
async def read_item_by_id(
    item_id: int,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve an item by its ID.

    Parameters:
    - item_id (int): The ID of the item to retrieve.
    - current_user (Users): The current user making the request.
    - db (Session): The database session.

    Returns:
    - item (Items): The retrieved item.

    Raises:
    - HTTPException: If the item is not found.

    """
    # Get the item instance
    item = (
        db.query(Items)
        .filter(Items.id == item_id)
        .filter(Items.user_id == current_user.id)
        .first()
    )
    if not item:
        logger.warning("Item %s not found", item_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )

    # Log the successful retrieval of the item
    logger.info("Item %s retrieved by user %s", item_id, current_user.id)

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
    Retrieve a list of items.

    This function retrieves a list of items from the database based on the
    provided parameters.
    It applies pagination to limit the number of items returned.

    Parameters:
    - skip (int): The number of items to skip. Default is 0.
    - limit (int): The maximum number of items to return. Default is 10.
    - current_user (Users): The current user. This parameter is injected by the
        `get_current_user` dependency.
    - db (Session): The database session. This parameter is injected by the `get_db` dependency.

    Returns:
    - List[ItemRead]: A list of items read from the database.

    Raises:
    - HTTPException: If the current user is inactive or no items are found.

    """

    # Ensure the current user is active
    if not current_user.is_active:
        logger.warning("Inactive user %s attempted to read items", current_user.id)
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

    logger.info("%d items read by user %s", len(items), current_user.id)

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
    Delete an item.

    Parameters:
    - item_id (int): The ID of the item to be deleted.
    - current_user (Users): The current user making the request.
    - db (Session): The database session.

    Returns:
    - ItemDelete: The deleted item ID.

    Raises:
    - HTTPException: If the current user is inactive, the item is not found, or
        there is an internal server error.
    """

    # Ensure the current user is active
    if not current_user.is_active:
        logger.warning(
            "Inactive user %s attempted to delete item %s", current_user.id, item_id
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
        logger.warning("Item %s not found", item_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )

    # Delete the item
    db.delete(item)

    try:
        # Commit the transaction
        db.commit()
        logger.info("Item %s deleted by user %s", item_id, current_user.id)
    except Exception as e:
        # Rollback in case of error
        db.rollback()
        logger.error("Error deleting item %s: %s", item_id, str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        ) from e

    # Return the deleted item ID
    return ItemDelete(id=item.id)
