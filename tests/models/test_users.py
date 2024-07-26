"""
This module contains tests for the User model.

The tests in this module validate the structure and constraints of the User model in the
database. It includes tests to confirm the presence of required tables, validate the
existence and data types of expected columns, verify nullable or not nullable fields,
test columns with specific constraints, ensure the correctness of default values,
validate column lengths, and enforce unique constraints for columns requiring unique values.
"""

from typing import Any

from sqlalchemy import Boolean, String
from sqlalchemy.dialects.postgresql import UUID


def test_model_structure_table_exists(db_inspector: Any):
    """
    Test to confirm the presence of the "users" table within the database schema.
    """
    assert db_inspector.has_table("users")


def test_model_structure_data_types(db_inspector: Any):
    """
    Test to validate the existence of expected columns in the "users" table,
    ensuring correct data types.
    """
    table = "users"
    columns = {column["name"]: column for column in db_inspector.get_columns(table)}

    assert isinstance(columns["id"]["type"], UUID)  # UUID type for id
    assert isinstance(columns["name"]["type"], String)
    assert isinstance(columns["email"]["type"], String)
    assert isinstance(columns["password"]["type"], String)
    assert isinstance(columns["is_active"]["type"], Boolean)
    assert isinstance(columns["role"]["type"], String)  # Assuming role is a String


def test_model_structure_nullable_constraints(db_inspector: Any):
    """
    Test to verify nullable or not nullable fields in the "users" table.
    """
    table = "users"
    columns = db_inspector.get_columns(table)
    expected_nullable = {
        "id": False,
        "name": False,
        "email": False,
        "password": False,
        "is_active": False,
        "role": False,  # Assuming role is not nullable
    }

    for column in columns:
        assert (
            column["nullable"] == expected_nullable[column["name"]]
        ), f"Column {column['name']} is not nullable as expected."


def test_model_structure_column_constraints(db_inspector: Any):
    """
    Test to ensure that columns with specific constraints are accurately defined in
    the "users" table.
    """
    table = "users"
    constraints = db_inspector.get_check_constraints(table)

    assert any(
        constraint["name"] == "users_name_length_check" for constraint in constraints
    )
    assert any(
        constraint["name"] == "users_email_length_check" for constraint in constraints
    )
    assert any(
        constraint["name"] == "users_password_length_check"
        for constraint in constraints
    )
    assert any(
        constraint["name"] == "users_role_validity_check" for constraint in constraints
    )  # Add check for role


def test_model_structure_default_values(db_inspector: Any):
    """
    Test to verify the correctness of default values for relevant columns in the "users" table.
    """
    table = "users"
    columns = {column["name"]: column for column in db_inspector.get_columns(table)}

    # Convert the default value to boolean if needed or directly compare with string values
    assert columns["is_active"]["default"].lower() == "false"


def test_model_structure_column_lengths(db_inspector: Any):
    """
    Test to ensure that column lengths in the "users" table align with defined requirements.
    """
    table = "users"
    columns = {column["name"]: column for column in db_inspector.get_columns(table)}

    assert columns["name"]["type"].length == 255
    assert columns["email"]["type"].length == 255
    assert columns["password"]["type"].length == 255
    assert columns["role"]["type"].length == 50  # Adjust length according to your model


def test_model_structure_unique_constraints(db_inspector: Any):
    """
    Test to validate the enforcement of unique constraints for columns requiring unique values
    in the "users" table.
    """
    table = "users"
    constraints = db_inspector.get_unique_constraints(table)

    assert any(constraint["name"] == "users_unique_email" for constraint in constraints)
    # Add any additional unique constraints if applicable
