"""
This module contains fixtures and utilities for testing.

Fixtures:
- client: The FastAPI test client.
- db_session: The database session for testing.

Utilities:
- pytest_collection_modifyitems: A utility function for modifying pytest collection items.
"""

from .fixtures import client, db_session
from .utils.pytest_utils import pytest_collection_modifyitems
