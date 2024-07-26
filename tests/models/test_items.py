"""
This module contains tests to validate the structure of the 'items' table in the database schema.
"""

from typing import Any

from sqlalchemy import Integer, String
from sqlalchemy.dialects.postgresql import UUID


def test_model_structure_table_exists(db_inspector: Any):
    """
    Test to confirm the presence of the 'items' table within the database schema.

    Args:
        db_inspector (Any): The database inspector object.

    Returns:
        None
    """
    assert db_inspector.has_table("items")


def test_model_structure_data_types(db_inspector: Any):
    """
    Test to validate the existence of expected columns in the 'items' table and
    ensure correct data types.

    Args:
        db_inspector (Any): The database inspector object.

    Returns:
        None
    """
    table = "items"
    columns = {column["name"]: column for column in db_inspector.get_columns(table)}

    assert isinstance(columns["id"]["type"], Integer)
    assert isinstance(columns["user_id"]["type"], UUID)  # UUID type for user_id
    assert isinstance(columns["name"]["type"], String)


def test_model_structure_nullable_constraints(db_inspector: Any):
    """
    Test to verify nullable or not nullable fields in the 'items' table.

    Args:
        db_inspector (Any): The database inspector object.

    Returns:
        None
    """
    table = "items"
    columns = db_inspector.get_columns(table)
    expected_nullable = {
        "id": False,
        "user_id": False,
        "name": False,
    }

    for column in columns:
        assert (
            column["nullable"] == expected_nullable[column["name"]]
        ), f"Column {column['name']} is not nullable as expected."


def test_model_structure_column_constraints(db_inspector: Any):
    """
    Test to verify columns with specific constraints in the 'items' table.

    Args:
        db_inspector (Any): The database inspector object.

    Returns:
        None
    """
    table = "items"
    constraints = db_inspector.get_check_constraints(table)

    assert any(
        constraint["name"] == "items_name_length_check" for constraint in constraints
    )


def test_model_structure_default_values(db_inspector: Any):
    """
    Test to verify the correctness of default values for relevant columns in the 'items' table.

    Args:
        db_inspector (Any): The database inspector object.

    Returns:
        None
    """
    table = "items"
    columns = {column["name"]: column for column in db_inspector.get_columns(table)}

    # Assuming there are no specific default values set for 'name' and 'user_id'
    assert columns["name"]["default"] is None
    assert columns["user_id"]["default"] is None


def test_model_structure_column_lengths(db_inspector: Any):
    """
    Test to ensure that column lengths in the 'items' table align with defined requirements.

    Args:
        db_inspector (Any): The database inspector object.

    Returns:
        None
    """
    table = "items"
    columns = {column["name"]: column for column in db_inspector.get_columns(table)}

    assert columns["name"]["type"].length == 255


def test_model_structure_unique_constraints(db_inspector: Any):
    """
    Test to validate the enforcement of unique constraints for columns requiring unique
    values in the 'items' table.

    Args:
        db_inspector (Any): The database inspector object.

    Returns:
        None
    """
    table = "items"
    constraints = db_inspector.get_unique_constraints(table)

    # Add unique constraints checks if any are defined for the 'items' table
    # For example, if 'name' should be unique
    assert not any(
        constraint["name"] == "items_unique_name" for constraint in constraints
    )


def test_model_structure_relationships(db_inspector: Any):
    """
    Test to validate relationships between tables in the database schema.

    Args:
        db_inspector (Any): The database inspector object.

    Returns:
        None
    """
    table = "items"
    foreign_keys = db_inspector.get_foreign_keys(table)

    # Check for the foreign key relationship between items.user_id and users.id
    assert any(
        fk["referred_table"] == "users"
        and fk["referred_columns"] == ["id"]
        and fk["constrained_columns"] == ["user_id"]
        for fk in foreign_keys
    ), "Foreign key constraint from items.user_id to users.id is missing or incorrect."

    # Check for the foreign key relationship between category_item_association.item_id and items.id
    table = "category_item_association"
    foreign_keys = db_inspector.get_foreign_keys(table)

    assert any(
        fk["referred_table"] == "items"
        and fk["referred_columns"] == ["id"]
        and fk["constrained_columns"] == ["item_id"]
        for fk in foreign_keys
    ), """Foreign key constraint from category_item_association.item_id
    to items.id is missing or incorrect."""
