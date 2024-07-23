from sqlalchemy import Integer, String, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID

"""
## Table and Column Validation
"""

"""
- [ ] Confirm the presence of all required tables within the database schema.
"""


def test_model_structure_table_exists(db_inspector):
    assert db_inspector.has_table("items")


"""
- [ ] Validate the existence of expected columns in each table, ensuring correct data types.
"""


def test_model_structure_data_types(db_inspector):
    table = "items"
    columns = {column["name"]: column for column in db_inspector.get_columns(table)}

    assert isinstance(columns["id"]["type"], Integer)
    assert isinstance(columns["user_id"]["type"], UUID)  # UUID type for user_id
    assert isinstance(columns["name"]["type"], String)


"""
- [ ] Verify nullable or not nullable fields
"""


def test_model_structure_nullable_constraints(db_inspector):
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


"""
- [ ] Test columns with specific constraints to ensure they are accurately defined.
"""


def test_model_structure_column_constraints(db_inspector):
    table = "items"
    constraints = db_inspector.get_check_constraints(table)

    assert any(
        constraint["name"] == "items_name_length_check" for constraint in constraints
    )


"""
- [ ] Verify the correctness of default values for relevant columns.
"""


def test_model_structure_default_values(db_inspector):
    table = "items"
    columns = {column["name"]: column for column in db_inspector.get_columns(table)}

    # Assuming there are no specific default values set for 'name' and 'user_id'
    assert columns["name"]["default"] is None
    assert columns["user_id"]["default"] is None


"""
- [ ] Ensure that column lengths align with defined requirements.
"""


def test_model_structure_column_lengths(db_inspector):
    table = "items"
    columns = {column["name"]: column for column in db_inspector.get_columns(table)}

    assert columns["name"]["type"].length == 255


"""
- [ ] Validate the enforcement of unique constraints for columns requiring unique values.
"""


def test_model_structure_unique_constraints(db_inspector):
    table = "items"
    constraints = db_inspector.get_unique_constraints(table)

    # Add unique constraints checks if any are defined for the 'items' table
    # For example, if 'name' should be unique
    assert not any(
        constraint["name"] == "items_unique_name" for constraint in constraints
    )


"""
- [ ] Validate relationships between tables.
"""


def test_model_structure_relationships(db_inspector):
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
        fk["referred_table"] == "items" and 
        fk["referred_columns"] == ["id"] and 
        fk["constrained_columns"] == ["item_id"]
        for fk in foreign_keys
    ), "Foreign key constraint from category_item_association.item_id to items.id is missing or incorrect."
