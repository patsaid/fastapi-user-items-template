"""
This module contains the API handlers for the category endpoints
"""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.routes.auth.tokens import get_current_user
from app.routes.category.models import Categories, CategoryItemAssociation
from app.routes.category.schemas import (
    CategoryCreate,
    CategoryDelete,
    CategoryRead,
    CategoryUpdate,
)
from app.routes.users.models import Users

logger = logging.getLogger("app")
categories_router = APIRouter(prefix="/categories", tags=["Categories"])


@categories_router.post(
    "/", response_model=CategoryRead, status_code=status.HTTP_201_CREATED
)
async def create_categories(
    payload: CategoryCreate,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new category.

    Args:
        payload (CategoryCreate): The payload containing the category information.
        current_user (Users, optional): The current user. Defaults to Depends(get_current_user).
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        Categories: The newly created category.

    Raises:
        HTTPException: If the current user is inactive or has insufficient permissions.
        HTTPException: If there is an internal server error during category creation.
    """
    # Ensure the current user is active
    if not current_user.is_active:
        logger.warning(
            "Inactive user %s attempted to create a category", current_user.id
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user"
        )

    # Check if the current user has the 'admin' role
    if current_user.role != "admin":
        logger.warning(
            "User %s attempted to create a category without proper permissions",
            current_user.id,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
        )

    # Create a new category instance
    new_category = Categories(
        name=payload.name,
    )

    # Add the new category to the session
    db.add(new_category)

    try:
        # Commit the transaction
        db.commit()
        # Refresh to get the latest state of the category (e.g., auto-generated fields)
        db.refresh(new_category)
        logger.info("Category %s created by user %s", new_category.id, current_user.id)
    except Exception as e:
        # Rollback in case of error
        db.rollback()
        logger.error("Error creating category: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        ) from e

    # Return the newly created category
    return new_category


@categories_router.put("/{category_id}", response_model=CategoryRead)
async def update_categories(
    category_id: int,
    payload: CategoryUpdate,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update a category with the given category_id.

    Parameters:
    - category_id (int): The ID of the category to update.
    - payload (CategoryUpdate): The updated category data.
    - current_user (Users): The current authenticated user.
    - db (Session): The database session.

    Returns:
    - CategoryRead: The updated category.

    Raises:
    - HTTPException: If the user is inactive or has insufficient permissions.
    - HTTPException: If the category with the given category_id is not found.
    - HTTPException: If there is an internal server error during the update.

    """

    # Ensure the current user is active
    if not current_user.is_active:
        logger.warning(
            "Inactive user %s attempted to update category %s",
            current_user.id,
            category_id,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user"
        )

    # Check if the current user has the 'admin' role
    if current_user.role != "admin":
        logger.warning(
            "User %s attempted to update a category %s without proper permissions",
            current_user.id,
            category_id,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
        )

    # Get the category instance
    category = db.query(Categories).filter(Categories.id == category_id).first()
    if not category:
        logger.warning("Category %s not found", category_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )

    # Update the category instance
    category.name = payload.name

    try:
        # Commit the transaction
        db.commit()
        # Refresh to get the latest state of the category (e.g., auto-generated fields)
        db.refresh(category)

        logger.info("Category %s updated by user %s", category.id, current_user.id)
    except Exception as e:
        # Rollback in case of error
        db.rollback()
        logger.error("Error updating category %s: %s", category_id, e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        ) from e

    # Return the updated category
    return CategoryRead(
        id=category.id,
        name=category.name,
    )


@categories_router.get("/{category_id}", response_model=CategoryRead)
async def read_category_by_id(
    category_id: int,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve a category by its ID.

    Parameters:
    - category_id (int): The ID of the category to retrieve.
    - current_user (Users): The current user making the request.
    - db (Session): The database session.

    Returns:
    - CategoryRead: The category information.

    Raises:
    - HTTPException: If the current user is inactive or if the category is not found.
    """

    # Ensure the current user is active
    if not current_user.is_active:
        logger.warning(
            "Inactive user %s attempted to read category %s",
            current_user.id,
            category_id,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user"
        )

    # Get the category instance
    category = db.query(Categories).filter(Categories.id == category_id).first()
    if not category:
        logger.warning("Category %s not found", category_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )

    logger.info("Category %s read by user %s", category.id, current_user.id)

    # Return the category
    return CategoryRead(
        id=category.id,
        name=category.name,
    )


@categories_router.get("/", response_model=List[CategoryRead])
async def read_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve a list of categories with pagination.

    Parameters:
    - skip (int): The number of categories to skip (default: 0).
    - limit (int): The maximum number of categories to retrieve (default: 10).
    - current_user (Users): The current authenticated user.
    - db (Session): The database session.

    Returns:
    - List[CategoryRead]: A list of CategoryRead objects representing the retrieved categories.

    Raises:
    - HTTPException: If the current user is inactive or no categories are found.

    """

    # Ensure the current user is active
    if not current_user.is_active:
        logger.warning("Inactive user %s attempted to read categories", current_user.id)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user"
        )

    # Get the categories with pagination
    categories = db.query(Categories).offset(skip).limit(limit).all()
    if not categories:
        logger.warning("No categories found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No categories found"
        )

    logger.info("%s categories read by user %s", len(categories), current_user.id)

    # Return the categories
    return [CategoryRead(id=category.id, name=category.name) for category in categories]


@categories_router.delete("/{category_id}", response_model=CategoryDelete)
async def delete_categories(
    category_id: int,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete a category with the given category_id.

    Parameters:
    - category_id (int): The ID of the category to delete.
    - current_user (Users): The current authenticated user.
    - db (Session): The database session.

    Returns:
    - CategoryDelete: The deleted category.

    Raises:
    - HTTPException: If the user is inactive or has insufficient permissions.
    - HTTPException: If the category with the given category_id is not found.
    - HTTPException: If there is an internal server error during the deletion.
    """

    # Ensure the current user is active
    if not current_user.is_active:
        logger.warning(
            "Inactive user %s attempted to delete category %s",
            current_user.id,
            category_id,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user"
        )

    # Check if the current user has the 'admin' role
    if current_user.role != "admin":
        logger.warning(
            "User %s attempted to delete category %s without proper permissions",
            current_user.id,
            category_id,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
        )

    # Get the category instance
    category = db.query(Categories).filter(Categories.id == category_id).first()
    if not category:
        logger.warning("Category %s not found", category_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )

    # Delete the associations in the association table
    db.query(CategoryItemAssociation).filter(
        CategoryItemAssociation.category_id == category_id
    ).delete(synchronize_session=False)

    # Delete the category
    db.delete(category)

    try:
        # Commit the transaction
        db.commit()
        logger.info("Category %s deleted by user %s", category.id, current_user.id)
    except Exception as e:
        # Rollback in case of error
        db.rollback()
        logger.error("Error deleting category %s: %s", category_id, e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        ) from e

    # Return the deleted category
    return CategoryDelete(
        id=category.id,
    )
