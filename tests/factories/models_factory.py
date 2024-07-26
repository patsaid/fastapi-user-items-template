"""
This module contains factory functions for generating random data for the models.
"""

import uuid
from itertools import count

from faker import Faker

faker = Faker()

id_counter = count(start=1)


def get_random_user_dict(id_: uuid.UUID = None):
    """
    Generate a random user dictionary.

    Args:
        id_ (uuid.UUID, optional): The ID of the user. Defaults to None.

    Returns:
        dict: A dictionary representing a random user with the following keys:
            - id: The ID of the user.
            - name: The name of the user.
            - email: The email of the user.
            - password: The password of the user.
            - is_active: A boolean indicating if the user is active.
            - role: The role of the user (either "user" or "admin").
    """
    if id_ is None:
        id_ = str(uuid.uuid4())
    return {
        "id": id_,
        "name": faker.name(),
        "email": faker.email(),
        "password": faker.password(),
        "is_active": faker.boolean(),
        "role": faker.random_element(elements=("user", "admin")),
    }


def get_random_item_dict(id_: int = None):
    """
    Generate a random item dictionary.

    Args:
        id_ (int, optional): The ID of the item. Defaults to None.

    Returns:
        dict: A dictionary representing a random item with the following keys:
            - id: The ID of the item.
            - user_id: The ID of the user who owns the item (as a UUID).
            - name: The name of the item.
            - categories: A list of category IDs associated with the item.
    """
    if id_ is None:
        id_ = next(id_counter)
    return {
        "id": id_,
        "user_id": str(uuid.uuid4()),  # User ID as UUID
        "name": faker.word(),
        "categories": [
            next(id_counter) for _ in range(faker.random_int(min=0, max=3))
        ],  # Random number of category IDs
    }


def get_random_category_dict(id_: int = None):
    """
    Generate a random category dictionary.

    Args:
        id_ (int, optional): The ID of the category. Defaults to None.

    Returns:
        dict: A dictionary representing a random category with the following keys:
            - id: The ID of the category.
            - name: The name of the category.
    """
    if id_ is None:
        id_ = next(id_counter)
    return {"id": id_, "name": faker.word()}
