
import uuid
from itertools import count
from faker import Faker

faker = Faker()

id_counter = count(start=1)

def get_random_user_dict(id_: uuid.UUID = None):
    if id_ is None:
        id_ = str(uuid.uuid4())
    return {
        "id": id_,
        "name": faker.name(),
        "email": faker.email(),
        "password": faker.password(),
        "is_active": faker.boolean(),
        "role": faker.random_element(elements=("user", "admin"))
    }

def get_random_item_dict(id_: int = None):
    if id_ is None:
        id_ = next(id_counter)
    return {
        "id": id_,
        "user_id": str(uuid.uuid4()),  # User ID as UUID
        "name": faker.word(),
        "categories": [next(id_counter) for _ in range(faker.random_int(min=0, max=3))]  # Random number of category IDs
    }

def get_random_category_dict(id_: int = None):
    if id_ is None:
        id_ = next(id_counter)
    return {
        "id": id_,
        "name": faker.word()
    }
