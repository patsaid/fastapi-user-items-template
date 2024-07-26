"""
This module contains fixtures for testing.
"""

import pytest
from sqlalchemy import inspect


@pytest.fixture(scope="function")
def db_inspector(db_session):
    """
    Returns the SQLAlchemy inspector object for the given database session.

    Parameters:
    - db_session: A function that returns a SQLAlchemy database session.

    Returns:
    - The SQLAlchemy inspector object for the database session's bind.

    Example usage:
    >>> session = create_session()
    >>> inspector = db_inspector(session)
    >>> tables = inspector.get_table_names()
    """
    return inspect(db_session().bind)
