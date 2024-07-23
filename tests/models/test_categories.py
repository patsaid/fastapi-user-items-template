from sqlalchemy import Integer, String, ForeignKey

"""
## Table and Column Validation
"""

"""
- [ ] Confirm the presence of all required tables within the database schema.
"""


def test_model_structure_table_exists(db_inspector):
    assert db_inspector.has_table("categories")
    assert db_inspector.has_table("category_item_association")


"""
- [ ] Validate the existence of expected columns in each table, ensuring correct data types.
"""


def test_model_structure_data_types(db_inspector):
    table = "categories"
    columns = {column["name"]: column for column in db_inspector.get_columns(table)}

    assert isinstance(columns["id"]["type"], Integer)
    assert isinstance(columns["name"]["type"], String)

    table = "category_item_association"
    columns = {column["name"]: column for column in db_inspector.get_columns(table)}

    assert isinstance(columns["category_id"]["type"], Integer)
    assert isinstance(columns["item_id"]["type"], Integer)


"""
- [ ] Verify nullable or not nullable fields.
"""


def test_model_structure_nullable_constraints(db_inspector):
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


"""
- [ ] Test columns with specific constraints to ensure they are accurately defined.
"""


def test_model_structure_column_constraints(db_inspector):
    table = "categories"
    constraints = db_inspector.get_check_constraints(table)

    assert any(
        constraint["name"] == "categories_name_length_check"
        for constraint in constraints
    )


"""
- [ ] Ensure that column lengths align with defined requirements.
"""


def test_model_structure_column_lengths(db_inspector):
    table = "categories"
    columns = {column["name"]: column for column in db_inspector.get_columns(table)}

    assert (
        columns["name"]["type"].length == 36
    )  # Adjust this if your length is different


"""
- [ ]  Validate the enforcement of unique constraints for columns requiring unique values.
"""


def test_model_structure_unique_constraints(db_inspector):
    table = "categories"
    constraints = db_inspector.get_unique_constraints(table)

    assert any(
        constraint["name"] == "categories_unique_name" for constraint in constraints
    )


"""
- [ ] Validate relationships between tables.
"""


def test_model_structure_relationships(db_inspector):
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
