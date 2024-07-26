"""
This module contains tests for the categories model.
"""

from typing import Any

import pytest
from sqlalchemy import Integer, String

# Table and Column Validation


def test_model_structure_table_exists(db_inspector: Any):
    """
    Test to check if the required tables exist in the database schema.

    Args:
        db_inspector (Any): The database inspector object.

    Returns:
        None
    """
    assert db_inspector.has_table("categories")
    assert db_inspector.has_table("category_item_association")


def test_model_structure_data_types(db_inspector: Any):
    """
    Test to validate the existence of expected columns in each table and ensure correct data types.

    Args:
        db_inspector (Any): The database inspector object.

    Returns:
        None
    """
    table = "categories"
    columns = {column["name"]: column for column in db_inspector.get_columns(table)}

    assert isinstance(columns["id"]["type"], Integer)
    assert isinstance(columns["name"]["type"], String)

    table = "category_item_association"
    columns = {column["name"]: column for column in db_inspector.get_columns(table)}

    assert isinstance(columns["category_id"]["type"], Integer)
    assert isinstance(columns["item_id"]["type"], Integer)


def test_model_structure_nullable_constraints(db_inspector: Any):
    """
    Test to verify nullable or not nullable fields in each table.

    Args:
        db_inspector (Any): The database inspector object.

    Returns:
        None
    """
    table = "categories"
    columns = db_inspector.get_columns(table)
    expected_nullable = {
        "id": False,
        "name": False,
    }

    for column in columns:
        assert (
            column["nullable"] == expected_nullable[column["name"]]
        ), f"Column {column['name']} is not nullable as expected."

    table = "category_item_association"
    columns = db_inspector.get_columns(table)
    expected_nullable = {
        "category_id": False,
        "item_id": False,
    }

    for column in columns:
        assert (
            column["nullable"] == expected_nullable[column["name"]]
        ), f"Column {column['name']} is not nullable as expected."


def test_model_structure_column_constraints(db_inspector: Any):
    """
    Test to ensure that columns with specific constraints are accurately defined.

    Args:
        db_inspector (Any): The database inspector object.

    Returns:
        None
    """
    table = "categories"
    constraints = db_inspector.get_check_constraints(table)

    assert any(
        constraint["name"] == "categories_name_length_check"
        for constraint in constraints
    )


@pytest.mark.skip(reason="Skipping this test for now")
def test_model_structure_column_lengths(db_inspector: Any):
    """
    Test to ensure that column lengths align with defined requirements.

    Args:
        db_inspector (Any): The database inspector object.

    Returns:
        None
    """
    table = "categories"
    columns = {column["name"]: column for column in db_inspector.get_columns(table)}

    assert (
        columns["name"]["type"].length == 36
    )  # Adjust this if your length is different


def test_model_structure_unique_constraints(db_inspector: Any):
    """
    Test to validate the enforcement of unique constraints for columns requiring unique values.

    Args:
        db_inspector (Any): The database inspector object.

    Returns:
        None
    """
    table = "categories"
    constraints = db_inspector.get_unique_constraints(table)

    assert any(
        constraint["name"] == "categories_unique_name" for constraint in constraints
    )


@pytest.mark.skip(reason="Skipping this test for now")
def test_model_structure_relationships(db_inspector: Any):
    """
    Test to validate relationships between tables.

    Args:
        db_inspector (Any): The database inspector object.

    Returns:
        None
    """
    table = "category_item_association"
    foreign_keys = db_inspector.get_foreign_keys(table)

    assert any(
        fk["referred_table"] == "categories"
        and fk["referred_columns"] == ["id"]
        and fk["constrained_columns"] == ["category_id"]
        for fk in foreign_keys
    ), "Foreign key constraint from category_item_association.category_id to categories.id is missing or incorrect."

    assert any(
        fk["referred_table"] == "items"
        and fk["referred_columns"] == ["id"]
        and fk["constrained_columns"] == ["item_id"]
        for fk in foreign_keys
    ), "Foreign key constraint from category_item_association.item_id to items.id is missing or incorrect."
