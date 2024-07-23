from sqlalchemy import Boolean, String
from sqlalchemy.dialects.postgresql import UUID

"""
## Table and Column Validation
"""

"""
- [ ] Confirm the presence of all required tables within the database schema.
"""

def test_model_structure_table_exists(db_inspector):
    assert db_inspector.has_table("users")


"""
- [ ] Validate the existence of expected columns in each table, ensuring correct data types.
"""

def test_model_structure_data_types(db_inspector):
    table = "users"
    columns = {column["name"]: column for column in db_inspector.get_columns(table)}

    assert isinstance(columns["id"]["type"], UUID)  # UUID type for id
    assert isinstance(columns["name"]["type"], String)
    assert isinstance(columns["email"]["type"], String)
    assert isinstance(columns["password"]["type"], String)
    assert isinstance(columns["is_active"]["type"], Boolean)
    assert isinstance(columns["role"]["type"], String)  # Assuming role is a String


"""
- [ ] Verify nullable or not nullable fields
"""

def test_model_structure_nullable_constraints(db_inspector):
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


"""
- [ ] Test columns with specific constraints to ensure they are accurately defined.
"""

def test_model_structure_column_constraints(db_inspector):
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


"""
- [ ] Verify the correctness of default values for relevant columns.
"""

def test_model_structure_default_values(db_inspector):
    table = "users"
    columns = {column["name"]: column for column in db_inspector.get_columns(table)}

    # Convert the default value to boolean if needed or directly compare with string values
    assert columns["is_active"]["default"].lower() == "false"


"""
- [ ] Ensure that column lengths align with defined requirements.
"""

def test_model_structure_column_lengths(db_inspector):
    table = "users"
    columns = {column["name"]: column for column in db_inspector.get_columns(table)}

    assert columns["name"]["type"].length == 255
    assert columns["email"]["type"].length == 255
    assert columns["password"]["type"].length == 255
    assert columns["role"]["type"].length == 50  # Adjust length according to your model


"""
- [ ] Validate the enforcement of unique constraints for columns requiring unique values.
"""

def test_model_structure_unique_constraints(db_inspector):
    table = "users"
    constraints = db_inspector.get_unique_constraints(table)

    assert any(constraint["name"] == "users_unique_email" for constraint in constraints)
    # Add any additional unique constraints if applicable

