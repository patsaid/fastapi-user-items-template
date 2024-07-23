import logging
from typing import List

from app.routes.category.models import Categories, Category_Item_association
from fastapi import Depends, HTTPException, Query, status, APIRouter
from app.routes.category.schemas import (
    CategoryCreate,
    CategoryRead,
    CategoryUpdate,
    CategoryDelete,
)
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.routes.auth.tokens import get_current_user
from app.routes.users.models import Users


logger = logging.getLogger("app")
categories_router = APIRouter(prefix="/categories", tags=["Categories"])


@categories_router.post("/", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
async def create_categories(
    payload: CategoryCreate,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    This API is used to create a category
    """

    # Ensure the current user is active
    if not current_user.is_active:
        logger.warning(
            f"Inactive user {current_user.id} attempted to create a category"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user"
        )

    # Check if the current user has the 'admin' role
    if current_user.role != "admin":
        logger.warning(
            f"User {current_user.id} attempted to create a category without proper permissions"
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
        logger.info(f"Category {new_category.id} created by user {current_user.id}")
    except Exception as e:
        # Rollback in case of error
        db.rollback()
        logger.error(f"Error creating category: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error"
        )

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
    This API is used to update a category
    """

    # Ensure the current user is active
    if not current_user.is_active:
        logger.warning(
            f"Inactive user {current_user.id} attempted to update category {category_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user"
        )

    # Check if the current user has the 'admin' role
    if current_user.role != "admin":
        logger.warning(
            f"User {current_user.id} attempted to update a category {category_id} without proper permissions"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
        )

    # Get the category instance
    category = db.query(Categories).filter(Categories.id == category_id).first()
    if not category:
        logger.warning(f"Category {category_id} not found")
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

        logger.info(f"Category {category.id} updated by user {current_user.id}")
    except Exception as e:
        # Rollback in case of error
        db.rollback()
        logger.error(f"Error updating category {category_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error"
        )

    # Return the updated category
    return CategoryRead(
        id=category.id,
        name=category.name,
    )


@categories_router.get("/{category_id}", response_model=CategoryRead)
async def read_categories(
    category_id: int,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    This API is used to read categories
    """

    # Ensure the current user is active
    if not current_user.is_active:
        logger.warning(
            f"Inactive user {current_user.id} attempted to read category {category_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user"
        )

    # Get the category instance
    category = db.query(Categories).filter(Categories.id == category_id).first()
    if not category:
        logger.warning(f"Category {category_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )

    logger.info(f"Category {category.id} read by user {current_user.id}")

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
    This API is used to read all categories with optional pagination
    """

    # Ensure the current user is active
    if not current_user.is_active:
        logger.warning(f"Inactive user {current_user.id} attempted to read categories")
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

    logger.info(f"{len(categories)} categories read by user {current_user.id}")

    # Return the categories
    return [CategoryRead(id=category.id, name=category.name) for category in categories]


@categories_router.delete("/{category_id}", response_model=CategoryDelete)
async def delete_categories(
    category_id: int,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    This API is used to delete a category
    """

    # Ensure the current user is active
    if not current_user.is_active:
        logger.warning(
            f"Inactive user {current_user.id} attempted to delete category {category_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user"
        )

    # Check if the current user has the 'admin' role
    if current_user.role != "admin":
        logger.warning(
            f"User {current_user.id} attempted to delete category {category_id} without proper permissions"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
        )

    # Get the category instance
    category = db.query(Categories).filter(Categories.id == category_id).first()
    if not category:
        logger.warning(f"Category {category_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )

    # Delete the associations in the association table
    db.query(Category_Item_association).filter(
        Category_Item_association.category_id == category_id
    ).delete(synchronize_session=False)

    # Delete the category
    db.delete(category)

    try:
        # Commit the transaction
        db.commit()
        logger.info(f"Category {category.id} deleted by user {current_user.id}")
    except Exception as e:
        # Rollback in case of error
        db.rollback()
        logger.error(f"Error deleting category {category_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error"
        )

    # Return the deleted category
    return CategoryDelete(
        id=category.id,
    )
